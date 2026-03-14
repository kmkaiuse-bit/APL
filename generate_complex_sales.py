"""
鵝媽媽 複雜版銷售數據生成器
生成 goose_mama_sales_complex.csv
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)

# ── 基本設定 ────────────────────────────────────────────────────────────────

weekdays_zh = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']

products = [
    # (產品名稱, 售價, 原材料成本)
    ('珍珠奶茶', 32, 12),
    ('芝士奶蓋', 45, 18),
    ('燒仙草',   38, 14),
    ('手工梳打', 28, 10),
    ('純茶',     22,  8),
]

branches = ['校門口', '圖書館旁']

# 每日氣溫（沿用原始數據）
temp_map = {
    '2025-09-01':31.5,'2025-09-02':30.8,'2025-09-03':33.2,'2025-09-04':32.7,
    '2025-09-05':31.0,'2025-09-06':30.5,'2025-09-07':34.1,'2025-09-08':32.9,
    '2025-09-09':29.3,'2025-09-10':31.7,'2025-09-11':33.5,'2025-09-12':34.2,
    '2025-09-13':30.1,'2025-09-14':28.6,'2025-09-15':31.2,'2025-09-16':30.8,
    '2025-09-17':32.4,'2025-09-18':29.6,'2025-09-19':28.3,'2025-09-20':30.5,
    '2025-09-21':33.7,'2025-09-22':31.9,'2025-09-23':29.4,'2025-09-24':30.7,
    '2025-09-25':32.1,'2025-09-26':28.8,'2025-09-27':30.2,'2025-09-28':31.8,
    '2025-09-29':33.4,'2025-09-30':32.0,
    '2025-10-01':30.6,'2025-10-02':31.3,'2025-10-03':29.8,'2025-10-04':28.4,
    '2025-10-05':30.1,'2025-10-06':32.5,'2025-10-07':33.0,'2025-10-08':31.7,
    '2025-10-09':29.3,'2025-10-10':27.8,'2025-10-11':30.2,'2025-10-12':31.5,
    '2025-10-13':28.6,'2025-10-14':30.9,'2025-10-15':32.1,'2025-10-16':27.5,
    '2025-10-17':26.8,'2025-10-18':29.4,'2025-10-19':28.1,'2025-10-20':30.7,
    '2025-10-21':25.3,'2025-10-22':27.6,'2025-10-23':29.2,'2025-10-24':28.8,
    '2025-10-25':30.4,'2025-10-26':24.1,'2025-10-27':25.9,'2025-10-28':27.4,
    '2025-10-29':29.6,'2025-10-30':31.2,'2025-10-31':26.3,
}

# 考試週（沿用原始：9月16-26日）
exam_dates = set(
    (date(2025, 9, 16) + timedelta(d)).strftime('%Y-%m-%d')
    for d in range(11)
)

# 公眾假期
ph_dates = {
    '2025-10-01',  # 國慶日
    '2025-10-06',  # 中秋節翌日
    '2025-10-29',  # 重陽節
}

# 雨天（約25%的日子）
rain_days = {
    '2025-09-09','2025-09-14','2025-09-18','2025-09-19','2025-09-23',
    '2025-09-26','2025-10-03','2025-10-04','2025-10-09','2025-10-10',
    '2025-10-16','2025-10-17','2025-10-19','2025-10-21','2025-10-26',
    '2025-10-27',
}

# 優惠活動
#   key: date_str  →  (優惠類型, 折扣率%)
promo_map = {}
for d in range(8, 13):    # 9月8-12日：學生折扣10%
    promo_map[f'2025-09-{d:02d}'] = ('學生折扣', 10)
for d in range(13, 18):   # 10月13-17日：季節特飲15%
    promo_map[f'2025-10-{d:02d}'] = ('季節特飲', 15)
promo_map['2025-09-21'] = ('買一送一', 0)   # 9月21日買一送一


# ── 輔助函數 ────────────────────────────────────────────────────────────────

def calc_base_sales(pname, temp, is_exam, is_rain, is_ph, is_promo,
                    promo_pct, is_weekend):
    """計算某產品的基礎銷量"""
    tn = (temp - 25) / 10          # 溫度標準化，約 -1 ~ +1

    if   pname == '珍珠奶茶': base = 35 + tn * 28
    elif pname == '芝士奶蓋': base = 22 + tn * 9
    elif pname == '燒仙草':   base = 35 - tn * 22  # 涼天更好賣
    elif pname == '手工梳打': base = 14 + tn * 7
    else:                      base =  4 + tn * 2   # 純茶

    if is_exam:    base *= 1.35
    if is_rain:
        if pname in ('珍珠奶茶', '芝士奶蓋', '手工梳打'):
            base *= 0.82
        elif pname == '燒仙草':
            base *= 1.18
    if is_ph:      base *= 0.45
    if is_promo:
        base *= (1 + promo_pct / 100 + 0.12)
        if promo_pct == 0:   # 買一送一
            base *= 1.35
    if is_weekend: base *= 0.72

    return base


# ── 生成數據 ────────────────────────────────────────────────────────────────

rows = []

d = date(2025, 9, 1)
while d <= date(2025, 10, 31):
    ds        = d.strftime('%Y-%m-%d')
    wd        = weekdays_zh[d.weekday()]
    temp      = temp_map[ds]
    is_exam   = ds in exam_dates
    is_rain   = ds in rain_days
    is_ph     = ds in ph_dates
    is_weekend = d.weekday() >= 5

    # 濕度：天熱偏低，下雨偏高
    humidity = round(82 - (temp - 25) * 0.9 + random.uniform(-3, 3)
                     + (10 if is_rain else 0))
    humidity = max(55, min(96, humidity))

    # 優惠
    if ds in promo_map:
        promo_type, promo_pct = promo_map[ds]
        is_promo = True
    else:
        promo_type, promo_pct, is_promo = '無', 0, False

    # 員工數目（日等級）
    if is_ph:
        staff = 1
    elif is_weekend:
        staff = random.choice([1, 2])
    elif is_exam:
        staff = random.choice([3, 3, 4])
    else:
        staff = random.choice([2, 2, 3])

    # 廣告費用（日等級）
    if is_promo:
        ad_spend = random.choice([200, 300, 400])
    elif is_exam:
        ad_spend = random.choice([100, 150])
    else:
        ad_spend = random.choice([0, 0, 50, 100])

    # 預估當天全分店總銷量（用於計算等候時間）
    est_total = sum(
        calc_base_sales(p, temp, is_exam, is_rain, is_ph, is_promo,
                        promo_pct, is_weekend)
        for p, _, _ in products
    )

    for branch in branches:
        # 分店比例
        if branch == '校門口':
            b_factor = 1.0
        else:
            b_factor = 0.85 if is_exam else 0.62

        branch_total = est_total * b_factor

        # 等候時間（分鐘）：總客量 ÷ 員工 × 係數
        wait_raw = branch_total * 0.09 / staff + random.uniform(-1.5, 2.5)
        wait_time = max(2, min(20, round(wait_raw)))

        # 顧客評分：等候愈長評分愈低，有優惠略高
        rating_raw = (4.5
                      - (wait_time - 5) * 0.05
                      + (0.15 if is_promo else 0)
                      + random.uniform(-0.2, 0.2))
        rating = round(max(3.0, min(5.0, rating_raw)), 1)

        for pname, price, cost in products:
            base = calc_base_sales(pname, temp, is_exam, is_rain, is_ph,
                                   is_promo, promo_pct, is_weekend)
            base *= b_factor
            sales = max(1, round(base + random.uniform(-2.5, 2.5)))

            # 實際售價（有折扣時）
            if promo_pct > 0:
                actual_price = round(price * (1 - promo_pct / 100))
            else:
                actual_price = price

            # 外賣 vs 堂食
            takeaway_rate = 0.22
            if is_rain:    takeaway_rate += 0.20
            if is_exam:    takeaway_rate += 0.08
            if is_weekend: takeaway_rate -= 0.05
            takeaway = max(0, round(sales * takeaway_rate + random.uniform(-1, 1)))
            dine_in  = max(0, sales - takeaway)

            # 新顧客比例
            new_cust = 20
            if is_promo:   new_cust = 38
            if is_exam:    new_cust = 14
            if is_weekend: new_cust = 28
            new_cust_pct = min(65, max(5,
                               round(new_cust + random.uniform(-5, 5))))

            # 庫存補充量（每日每產品，非考試週周末補少些）
            if is_ph:
                restock = 0
            elif is_exam:
                restock = random.choice([80, 100, 120])
            elif is_weekend:
                restock = random.choice([40, 60])
            else:
                restock = random.choice([60, 80, 100])

            rows.append({
                '日期':          ds,
                '星期':          wd,
                '分店':          branch,
                '產品名稱':      pname,
                '氣溫_攝氏':     temp,
                '濕度_百分比':   humidity,
                '是否落雨':      '是' if is_rain   else '否',
                '是否考試週':    '是' if is_exam   else '否',
                '是否公眾假期':  '是' if is_ph     else '否',
                '是否有優惠':    '是' if is_promo  else '否',
                '優惠類型':      promo_type,
                '售價_港幣':     actual_price,
                '原材料成本_港幣': cost,
                '銷量':          sales,
                '外賣訂單數':    takeaway,
                '堂食訂單數':    dine_in,
                '顧客評分':      rating,
                '候客時間_分鐘': wait_time,
                '員工數目':      staff,
                '廣告費用_港幣': ad_spend,
                '新顧客比例_百分比': new_cust_pct,
                '庫存補充量':    restock,
            })

    d += timedelta(days=1)

# ── 輸出 CSV ────────────────────────────────────────────────────────────────

fieldnames = [
    '日期', '星期', '分店', '產品名稱',
    '氣溫_攝氏', '濕度_百分比', '是否落雨',
    '是否考試週', '是否公眾假期', '是否有優惠', '優惠類型',
    '售價_港幣', '原材料成本_港幣',
    '銷量', '外賣訂單數', '堂食訂單數',
    '顧客評分', '候客時間_分鐘', '員工數目',
    '廣告費用_港幣', '新顧客比例_百分比', '庫存補充量',
]

output_path = 'goose_mama_sales_complex.csv'
with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'Done: {len(rows)} rows -> {output_path}')
