"""
鵝媽媽 複雜版顧客評論生成器
生成 reviews_complex.csv（100 行 × 10 欄）

隱藏規律：
1. 等候時間越長 → 評分越低
2. 考試週 → 回頭客比例高、負評少
3. 校門口 vs 圖書館旁：等候時間分佈不同（校門口較長）
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)

# ── 基本設定 ──────────────────────────────────────────────────────────────────

products = ['珍珠奶茶', '芝士奶蓋', '燒仙草', '手工梳打', '純茶']
branches = ['校門口', '圖書館旁']
customer_types = ['學生', '教職員', '外來客']
customer_weights = [0.65, 0.20, 0.15]

# 考試週：9月16-26日
exam_dates_set = set(
    (date(2025, 9, 16) + timedelta(d)).strftime('%Y-%m-%d')
    for d in range(11)
)

# 全部日期（9月1日至10月31日）
all_dates = []
d = date(2025, 9, 1)
while d <= date(2025, 10, 31):
    all_dates.append(d.strftime('%Y-%m-%d'))
    d += timedelta(days=1)

# ── 評論模板（按評分類型分組）──────────────────────────────────────────────────

# 正面評論（4-5 星）
positive_reviews = [
    '{product}係我最愛，珍珠好彈牙，甜度啱啱好！',
    '{product}芝士層好厚好香，下次一定再嚟！',
    '{product}好清甜唔膩，夏天飲啱晒！',
    '珍珠係自家製，{product}食落真係唔同，好彈牙！',
    '{product}同男友一齊嚟都係點呢個，係最愛！',
    '{product}份量足，性價比高，下次再試！',
    '{product}係全區最好味，一定要試！',
    '{product}好值，份量足，下次帶朋友嚟試！',
    '{product}好大粒彈牙，係近年飲過最好嘅！',
    '{product}唔係太甜，啱我口味，係呢度最常點嘅。',
    '{product}每週都嚟買，係附近最好飲嘅！',
    '{product}係少數做得好嘅，唔係每間都有咁高質。',
    '{product}係朋友介紹嚟，試完即刻愛上，之後每週都嚟！',
    '{product}唔係普通奶茶，係要試嘅特別款！',
    '{product}好清爽，係健康之選！',
    '{product}係同學中最多人點嘅，係鵝媽媽嘅代表作！',
    '{product}好飲，呢度嘅品質真係有保證！',
    '{product}係我帶朋友嚟必介紹嘅款式，好香滑。',
    '今日等候時間只需 {wait} 分鐘，{product}出單快又好味，大讚！',
    '等咗 {wait} 分鐘就拎到{product}，超值！下次仲會再嚟。',
    '{product}好適合唔想太甜嘅人，又健康，好評！',
    '今次唔使等太耐，{wait} 分鐘就有{product}，滿意！',
    '{product}好好飲，放學一定嚟買，係我嘅日常！',
    '等咗 {wait} 分鐘，{product}好味，值得等！',
    '考試期間嚟買{product}，唔使等太耐，精神好返晒！',
]

# 中性評論（3 星）
neutral_reviews = [
    '{product}好味，但係等咗 {wait} 分鐘，有啲耐。',
    '等咗 {wait} 分鐘先出到單，{product}味道算係唔錯。',
    '{product}一般，等候時間 {wait} 分鐘係可以接受嘅範圍。',
    '今次等咗 {wait} 分鐘，{product}品質正常，下次再試。',
    '{product}算好味，等候時間中等，{wait} 分鐘左右。',
    '等咗 {wait} 分鐘，{product}好在飲品好味，否則唔會再嚟。',
    '{product}味道唔錯，但係出單速度可以改善。',
    '等候時間 {wait} 分鐘，{product}品質尚可，總體算滿意。',
]

# 負面評論（1-2 星）
negative_reviews = [
    '等咗 {wait} 分鐘先出到單，好難頂。',
    '{product}好味，但係等咗 {wait} 分鐘，有啲耐。',
    '出單好慢，等咗 {wait} 分鐘差啲趕唔切搭車。',
    '等咗超過 {wait} 分鐘，工作人員話係忙，希望改善。',
    '出單慢係一個大問題，等咗 {wait} 分鐘，已見到有客因為等太耐而走咗。',
    '出單要等近 {wait} 分鐘，影響咗我同朋友嘅計劃。',
    '等咗 {wait} 分鐘，好在{product}好味，否則唔會再嚟。',
    '出單慢令我放學後買完趕唔切去補習，等咗 {wait} 分鐘！',
    '等咗 {wait} 分鐘，朋友都唔想等走咗，之後可能唔會再嚟。',
    '出單慢已係好多人嘅投訴，等咗 {wait} 分鐘，希望老闆改善流程。',
    '等咗 {wait} 分鐘先拎到飲品，第一次嚟下次要考慮係咪再嚟。',
    '出單慢減一星，{product}本身好值得五星，可惜等咗 {wait} 分鐘！',
    '等咗近 {wait} 分鐘，{product}好味但係時間成本太高。',
    '等咗 {wait} 分鐘，老闆要認真考慮加人手或改善流程。',
    '出單慢係致命弱點，好味但係留唔住趕時間嘅客人，等咗 {wait} 分鐘！',
    '等咗 {wait} 分鐘，下次寧願去其他店，雖然唔及呢度好味。',
    '整體等候時間太長，等咗 {wait} 分鐘，希望可以做網上落單。',
]


def get_wait_time(branch):
    """按分店決定等候時間分佈。校門口較長，圖書館旁較短。"""
    if branch == '校門口':
        # 均值約 22 分鐘，範圍 8-40
        return max(8, min(40, round(random.gauss(22, 8))))
    else:
        # 均值約 12 分鐘，範圍 3-22
        return max(3, min(22, round(random.gauss(12, 5))))


def get_rating(wait_time, is_exam):
    """等候時間越長評分越低；考試週評分略高（熟客居多）。"""
    if wait_time <= 8:
        base = random.choices([5, 4], weights=[0.65, 0.35])[0]
    elif wait_time <= 15:
        base = random.choices([5, 4, 3], weights=[0.30, 0.50, 0.20])[0]
    elif wait_time <= 25:
        base = random.choices([4, 3, 2], weights=[0.25, 0.50, 0.25])[0]
    elif wait_time <= 35:
        base = random.choices([3, 2, 1], weights=[0.20, 0.55, 0.25])[0]
    else:
        base = random.choices([2, 1], weights=[0.40, 0.60])[0]

    # 考試週：評分略高（熟客較少抱怨）
    if is_exam and base < 5:
        if random.random() < 0.30:
            base = min(5, base + 1)

    return base


def get_review_text(product, wait_time, rating):
    """根據評分挑選對應類型的評論模板，替換佔位符。"""
    if rating >= 4:
        template = random.choice(positive_reviews)
    elif rating == 3:
        template = random.choice(neutral_reviews)
    else:
        template = random.choice(negative_reviews)

    return template.format(product=product, wait=wait_time)


# ── 生成 100 條評論 ────────────────────────────────────────────────────────────

rows = []

for i in range(1, 101):
    review_num = f'#{i:02d}'

    # 隨機日期
    ds = random.choice(all_dates)
    is_exam = ds in exam_dates_set

    # 分店（各50條）
    branch = branches[(i - 1) % 2]

    # 產品（按評論編號循環分配，確保各產品都有）
    product = products[(i - 1) % len(products)]

    # 等候時間
    wait = get_wait_time(branch)

    # 評分
    rating = get_rating(wait, is_exam)

    # 顧客類型
    ctype = random.choices(customer_types, weights=customer_weights)[0]

    # 是否回頭客：考試週回頭客比例更高
    if is_exam:
        returning = random.choices(['是', '否'], weights=[0.72, 0.28])[0]
    else:
        returning = random.choices(['是', '否'], weights=[0.45, 0.55])[0]

    # 評論內容
    review_text = get_review_text(product, wait, rating)

    rows.append({
        '評論編號':      review_num,
        '日期':          ds,
        '分店':          branch,
        '產品名稱':      product,
        '評分_星數':     rating,
        '等候時間_分鐘': wait,
        '顧客類型':      ctype,
        '是否回頭客':    returning,
        '是否考試週':    '是' if is_exam else '否',
        '評論內容':      review_text,
    })

# ── 輸出 CSV ──────────────────────────────────────────────────────────────────

fieldnames = [
    '評論編號', '日期', '分店', '產品名稱',
    '評分_星數', '等候時間_分鐘', '顧客類型',
    '是否回頭客', '是否考試週', '評論內容',
]

output_path = 'reviews_complex.csv'
with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'Done: {len(rows)} rows -> {output_path}')

# ── 快速驗證隱藏規律 ──────────────────────────────────────────────────────────

print('\n=== 隱藏規律驗證 ===')

# 規律1：等候時間 vs 評分
short_wait = [r for r in rows if r['等候時間_分鐘'] <= 15]
long_wait  = [r for r in rows if r['等候時間_分鐘'] > 25]
if short_wait:
    avg_short = sum(r['評分_星數'] for r in short_wait) / len(short_wait)
    print(f'等候 ≤15 分鐘平均評分：{avg_short:.2f}（樣本：{len(short_wait)}）')
if long_wait:
    avg_long = sum(r['評分_星數'] for r in long_wait) / len(long_wait)
    print(f'等候 >25 分鐘平均評分：{avg_long:.2f}（樣本：{len(long_wait)}）')

# 規律2：考試週 vs 回頭客
exam_rows   = [r for r in rows if r['是否考試週'] == '是']
normal_rows = [r for r in rows if r['是否考試週'] == '否']
if exam_rows:
    exam_return = sum(1 for r in exam_rows if r['是否回頭客'] == '是') / len(exam_rows)
    print(f'考試週回頭客比例：{exam_return:.0%}（樣本：{len(exam_rows)}）')
if normal_rows:
    norm_return = sum(1 for r in normal_rows if r['是否回頭客'] == '是') / len(normal_rows)
    print(f'非考試週回頭客比例：{norm_return:.0%}（樣本：{len(normal_rows)}）')

# 規律3：分店 vs 等候時間
for b in branches:
    b_rows = [r for r in rows if r['分店'] == b]
    avg_wait = sum(r['等候時間_分鐘'] for r in b_rows) / len(b_rows)
    print(f'{b} 平均等候時間：{avg_wait:.1f} 分鐘（樣本：{len(b_rows)}）')
