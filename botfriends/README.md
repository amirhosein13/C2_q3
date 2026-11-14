# botfriends — دوستان ربات

منبع: «Bot Friends 2» (مسابقه‌ی سبک ICPC؛ نسخه‌ی اصلی چندتستی با $\sum N\le5\cdot10^5$ و $\sum M\le10^6$).
نوع: **Batch با grader**. تابع:

```
long long min_cost(int N, int M, std::vector<long long> A,
                   std::vector<int> U, std::vector<int> V, std::vector<int> W)
```

تابع برای هر تست یک بار صدا زده می‌شود. زبان: C++.

## حل (model.cpp)

- $D(i,j)=d(i,j)+A_i+A_j$ را تعریف کنید. جواب برابر است با
  $\mathrm{MST}(D)-\sum A+\min A$.
- کران بالا (ساختی): درخت را با ریشه‌ی $\arg\min A$ پس‌ترتیب طی کنید. هر ربات به پدرش می‌رود و آنجا ادغام می‌شود.
- MST روی گراف کامل $D$ با روش Mehlhorn ساخته می‌شود:
  - به هر رأس $i$ یک برگ مجازی با یال $A_i$ وصل کنید و Dijkstra چندمبدئی بزنید.
  - کاندیدها:
    - یال‌های بین دو ناحیه‌ی Voronoi، با وزن $d_u+w+d_v$؛
    - یال برگ $A_i+d_i$، برای رأسی که مالک خودش نیست.
  - روی کاندیدها Kruskal بزنید.
- پیچیدگی: $O((N+M)\log N)$.
- درستی:
  - کران بالا اثبات شده است.
  - کران پایین فقط در حد طرح اثبات است (حالت دور در «درخت گذرگاه‌ها» کامل نشده).
  - فرمول با brute force روی فرایند واقعی (Dijkstra روی همه‌ی چندمجموعه‌های مکان ربات‌ها) چک شده است: بیش از ۱۵۰۰۰ گراف تصادفی با $n\le7$، و `tps stress` با ۳۰۰ دور. هیچ اختلافی نبود.

## زیرمسئله‌ها

| # | نام TPS | امتیاز | قید | شمول |
|---|---|---|---|---|
| 0 | samples | 0 | نمونه‌ها | — |
| 1 | equal_a | 8 | همه‌ی $A[i]$ برابر | small_eq |
| 2 | a_le_w | 12 | $\max A\le\min W$ | small_aw |
| 3 | n400 | 15 | $N\le400$، $M\le1000$ | samples، small_eq، small_aw |
| 4 | n3000 | 20 | $N\le3000$، $M\le6000$ | n400 |
| 5 | full | 45 | $N\le2\cdot10^5$، $M\le5\cdot10^5$ | equal_a، a_le_w، n3000 |

محدودیت‌ها: **۴ ثانیه** و **۵۱۲ مگابایت**.
- قیدهای کلی: $1\le A\le10^{12}$، $1\le W\le10^9$، گراف همبند، یال چندگانه مجاز.
- چرا TL برابر ۴ ثانیه است: راه‌حل هدف زیرمسئله‌ی ۴ (Dijkstra از هر رأس) حداکثر حدود ۲٫۱ ثانیه طول می‌کشد. Floyd روی گراف‌های تصادفی با $N=3000$ بیش از ۹ ثانیه طول می‌کشد. با این TL هر دو حدود ۲ برابر با مرز فاصله دارند.

## checker و grader

- **grader داوری:** کل ورودی را می‌خواند و `stdin` را می‌بندد، بعد تابع را صدا می‌زند. سپس به ترتیب رشته‌ی مخفی، `OK` و جواب را چاپ می‌کند.
- **checker (testlib، پروتکل CMS):**
  1. رشته‌ی مخفی را چک می‌کند؛ اگر نباشد، Protocol Violation با امتیاز ۰.
  2. خط وضعیت را چک می‌کند؛ هر چیزی جز `OK` یعنی WA.
  3. یک عدد int64 را می‌خواند و دقیق مقایسه می‌کند.
  4. خروجی اضافه، ناقص یا غیرعددی WA است.
  5. جواب گواهی ندارد، پس جواب کمتر از داور هم WA است، نه خطای داوری.
- `checker/run_checker_tests.sh` با ۲۲ خروجی دست‌ساز اجرا می‌شود و همه پاس می‌شوند.

## نتیجه‌ی `tps invoke` (TL = 4s، روی این ماشین)

| راه‌حل | samples | equal_a (8) | a_le_w (12) | n400 (15) | n3000 (20) | full (45) | جمع | مطابق انتظار |
|---|---|---|---|---|---|---|---|---|
| model.cpp | AC | AC | AC | AC | AC | AC | 100 | ✓ |
| boruvka.cpp (مستقل، $O(M\log^2N)$) | AC | AC | AC | AC | AC | AC | 100 | ✓ |
| dijkstra_each.cpp ($O(NM\log N)$) | AC | TLE | TLE | AC | AC | TLE | 35 | ✓ |
| floyd.cpp ($O(N^3)$) | AC | RE | RE | AC | TLE | RE | 15 | ✓ |
| slow_spfa.cpp (SPFA به‌جای Dijkstra) | AC | AC | AC | AC | AC | TLE | 55 | ✓ |
| sub2_vertex_weights.cpp (Kruskal با $w+A_u+A_v$) | WA | AC | AC | WA | WA | WA | 20 | ✓ |
| sub1_equal_a.cpp | WA | AC | WA | WA | WA | WA | 8 | ✓ |
| brute_states.cpp (فرایند کامل) | AC | RE | RE | RE | RE | RE | 0 | ✓ |
| wrong_no_leaf_edges.cpp | WA | AC | AC | WA | WA | WA | 20 | ✓ |
| wrong_union_vertices.cpp | WA | AC | AC | WA | WA | WA | 20 | ✓ |
| wrong_int_a.cpp ($A$ در int) | AC | WA | AC | WA | WA | WA | 12 | ✓ |
| wrong_root0.cpp (ریشه رأس ۰) | WA | AC | WA | WA | WA | WA | 8 | ✓ |
| wrong_star_min_a.cpp (همه به ارزان‌ترین رأس) | AC | WA | WA | WA | WA | WA | 0 | ✓ |
| wrong_selfish.cpp | WA | WA | WA | WA | WA | WA | 0 | ✓ |

زمان‌ها:
- model: حداکثر 0.47s، یعنی حدود ۸ برابر کمتر از TL.
- boruvka: حداکثر 2.6s.
- dijkstra_each در n3000: حداکثر 2.1s.
- floyd در n3000 به سقف hard limit می‌رسد.
- چهار تست ضد SPFA (`hidchain*` و `pathdec`) هفت نوع SPFA را رد می‌کنند: ترتیب‌های مختلف صف و SLF.

`tps stress` بدون hack بود: brute روی ۳۰۰ دور با $n\le6$، و boruvka روی ۱۵۰ دور با $n\le3000$.

**زمان‌بندی نهایی باید روی خود سرور CMS دوباره چک شود.**

## آپلود در CMS (فقط پنل ادمین، نسخه‌ی 1.5.1)

داخل همین پوشه:

```bash
tps gen
```
```bash
../tools/statement-pdf/build.sh statement/index.md statement/botfriends-fa.pdf
```
```bash
python3 ../tools/cms_upload.py statement/botfriends-fa.pdf
```

خروجی در `cms-upload/` است و مقدار تک‌تک فیلدهای پنل در `cms-upload/SETTINGS.md` آمده.

زیرمسئله‌ی نمونه‌ها (امتیاز ۰) در پارامترهای GroupMin نیست. CMS 1.5.1 زیرمسئله‌ها را بر اساس جایگاهشان شماره می‌زند، پس با آن، شماره‌ی همه‌ی زیرمسئله‌ها یکی جابه‌جا می‌شد. تست‌های نمونه همچنان داخل زیرمسئله‌های ۳ تا ۵ داوری می‌شوند.
