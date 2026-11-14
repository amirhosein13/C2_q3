# راهنمای گام‌به‌گام آپلود سوال «دوستان ربات» در CMS 1.5.1

این راهنما برای وقتی است که **فقط به پنل ادمین CMS** دسترسی دارید و به ترمینال سرور دسترسی ندارید.
همه‌ی کارها از مرورگر انجام می‌شود. فقط ساخت فایل‌ها روی کامپیوتر خودتان است.

مقدار دقیق تک‌تک فیلدها در فایل `cms-upload/SETTINGS.md` هم آمده است.
این راهنما همان‌ها را به ترتیب انجام‌دادن توضیح می‌دهد.

---

## گام ۰: آماده کردن فایل‌ها روی کامپیوتر خودتان

به لینوکس (یا WSL روی ویندوز) با `git`، `g++`، `python3`، `make` و `zip` نیاز دارید.

۱. ریپو را بگیرید و به شاخه‌ی سوال بروید:

```bash
git clone https://github.com/amirhosein13/C2_q3.git
```
```bash
cd C2_q3 && git checkout claude/upbeat-bardeen-7il9ed
```

۲. اگر پوشه‌ی `tps/` خالی است، پرش کنید:

```bash
git submodule update --init
```

۳. TPS و پیش‌نیازهایش را نصب کنید (فقط بار اول):

```bash
cd tps && sudo ./install-tps.sh && cd ..
```
```bash
pip install psutil
```
```bash
sudo apt install dos2unix
```

۴. وارد پوشه‌ی سوال شوید، تست‌ها را بسازید و بسته‌ی آپلود را درست کنید:

```bash
cd botfriends
```
```bash
tps gen
```
```bash
python3 ../tools/cms_upload.py statement/botfriends-fa.pdf
```

`tps gen` حدود یک دقیقه طول می‌کشد. در پایان باید پوشه‌ی `botfriends/cms-upload/` با این محتوا ساخته شده باشد:

| فایل | کاربرد |
|---|---|
| `SETTINGS.md` | مقدار همه‌ی فیلدهای پنل |
| `statement-fa.pdf` | متن سوال |
| `attachments/botfriends.zip` | بسته‌ی شرکت‌کننده‌ها: grader نمونه، هدر، قالب کد و مثال‌ها |
| `managers/grader.cpp` | grader داوری |
| `managers/botfriends.h` | هدر |
| `managers/checker` | checker کامپایل‌شده (فایل اجرایی لینوکس) |
| `testcases-part1.zip`، `testcases-part2.zip`، `testcases-part3.zip` | ۶۹ تست در سه بخش، هر کدام زیر ۷۰ مگابایت |
| `score_type_parameters.json` | پارامترهای زیرمسئله‌ها |

> اگر نمی‌خواهید تست‌ها را خودتان بسازید، بقیه‌ی فایل‌ها (به‌جز zipهای تست) را جدا هم گرفته‌اید.
> ولی zipهای تست را حتماً باید با همین دستورها بسازید.

---

## گام ۱: قبل از شروع، از مدیر سرور بپرسید

1. **سطح دسترسی حساب شما** باید کامل (all) باشد تا بتوانید سوال بسازید.
2. **محدودیت حجم آپلود:** اگر جلوی پنل ادمین nginx هست، `client_max_body_size` باید حداقل `100M` باشد. این مقدار پیش‌فرض نمونه‌ی خود CMS است.
3. **زبان C++:** کدام نسخه‌های C++ برای آزمون فعال هستند.

---

## گام ۲: ساخت سوال

1. منوی سمت چپ پنل → **Tasks** → ساخت سوال جدید.
2. در جعبه‌ی **Name** بنویسید `botfriends` و سوال را بسازید.
3. صفحه‌ی سوال باز می‌شود. بقیه‌ی گام‌ها در همین صفحه است.

---

## گام ۳: بخش بالای صفحه (Task configuration)

| فیلد | مقدار |
|---|---|
| Title | `دوستان ربات` |
| Submission format | باید خودش `botfriends.%l` باشد؛ اگر نیست، همین را بنویسید |
| Feedback level | `Full` |
| Token mode | `Disabled` |
| Maximum number of submissions | `50` |
| Maximum number of user tests | `50` |
| Minimum interval between submissions | `60` |
| Minimum interval between user tests | `60` |
| Score decimal places | `2` |
| **Score mode** | **Use the sum over each subtask of the best result for that subtask across all submissions (IOI 2017-)** |

> **Score mode خیلی مهم است.** پیش‌فرض CMS گزینه‌ی دیگری است. با پیش‌فرض، امتیاز شرکت‌کننده از
> «آخرین ارسال» حساب می‌شود، نه بهترین نتیجه‌ی هر زیرمسئله.

**متن سوال:**
1. جلوی **Statements** روی **[add]** بزنید.
2. Language code: `fa`، فایل: `statement-fa.pdf` → **Upload**.
3. برگردید به صفحه‌ی سوال و تیک **Primary?** جلوی `fa` را بزنید.

**پیوست:** جلوی **Attachments** روی **[add]** بزنید و فایل `attachments/botfriends.zip` را آپلود کنید.

---

## گام ۴: بخش dataset (پایین همان صفحه)

| فیلد | مقدار |
|---|---|
| Time limit | `4` |
| Memory limit | `512` |
| Task type | `Batch` |
| Compilation | `Submissions are compiled with a grader` |
| Input file | **خالی** |
| Output file | **خالی** |
| Output evaluation | `Outputs are compared by a comparator` |
| Score Type | `GroupMin` |

**Managers:** جلوی **Managers** روی **[add]** بزنید و این سه فایل را از پوشه‌ی `managers/` یکی‌یکی آپلود کنید:
- `grader.cpp`
- `botfriends.h`
- `checker`

اسم فایل‌ها نباید عوض شود. CMS دقیقاً دنبال فایلی به اسم `checker` و `grader.cpp` می‌گردد.

---

## گام ۵: آپلود تست‌ها

1. در صفحه‌ی سوال روی **Add multiple testcases** بزنید.
2. فرم را این‌طور پر کنید:

| فیلد | مقدار |
|---|---|
| Archive | `testcases-part1.zip` |
| Public | تیک نزنید |
| Overwrite existing testcases | تیک نزنید |
| Input file names template | `*.in` |
| Output file names template | `*.out` |

3. **Upload** بزنید.
4. همین کار را برای `testcases-part2.zip` و `testcases-part3.zip` تکرار کنید.

> مقدار پیش‌فرض الگوها `input.*` و `output.*` است. **حتماً** آن‌ها را به `*.in` و `*.out` تغییر دهید،
> وگرنه هیچ تستی اضافه نمی‌شود.

در پایان، در جدول Test cases صفحه‌ی سوال باید **۶۹ تست** ببینید: ۳۸ از بخش اول، ۱۳ از بخش دوم و ۱۸ از بخش سوم.

---

## گام ۶: پارامترهای زیرمسئله‌ها

1. فایل `score_type_parameters.json` را با یک ویرایشگر متن باز کنید و **کل محتوایش** را کپی کنید.
2. در صفحه‌ی سوال، آن را در جعبه‌ی **Score type parameters** بچسبانید (Score Type باید `GroupMin` باشد).
3. پایین صفحه **Update** بزنید.

این پارامترها پنج زیرمسئله‌ی متن سوال را می‌سازند:

| در CMS | امتیاز | تعداد تست |
|---|---|---|
| Subtask 1 | 8 | 13 |
| Subtask 2 | 12 | 11 |
| Subtask 3 | 15 | 26 |
| Subtask 4 | 20 | 36 |
| Subtask 5 | 45 | 69 |

> نمونه‌ها (امتیاز ۰) عمداً زیرمسئله‌ی جدا نیستند. CMS زیرمسئله‌ها را به ترتیب شماره می‌زند و اگر نمونه‌ها
> جدا بودند، شماره‌ی همه‌ی زیرمسئله‌ها با متن سوال یکی اختلاف پیدا می‌کرد. تست‌های نمونه داخل
> زیرمسئله‌های ۳ تا ۵ داوری می‌شوند.

> CMS هنگام Update فقط چک می‌کند که متن JSON معتبر باشد. اگر چیزی اشتباه کپی شده باشد، خطا
> موقع داوری ظاهر می‌شود. به همین دلیل گام ۸ (ارسال آزمایشی) لازم است.

---

## گام ۷: اضافه کردن سوال به آزمون

1. صفحه‌ی آزمون → **Tasks** → سوال `botfriends` را اضافه کنید.
2. در تنظیمات آزمون، در **Allowed languages** فقط زبان‌های C++ (g++) را فعال بگذارید. grader فقط C++ دارد.

---

## گام ۸: ارسال آزمایشی (حتماً قبل از آزمون)

با یک کاربر آزمایشی که در رده‌بندی پنهان است (Hidden)، این فایل‌ها را از پوشه‌ی `botfriends/` ارسال کنید:

| فایل | امتیاز مورد انتظار |
|---|---|
| `solution/model.cpp` | **100** |
| `solution/boruvka.cpp` | 100 |
| `solution/slow_spfa.cpp` | 55 (فقط زیرمسئله‌ی ۵ را TLE می‌گیرد) |
| `solution/dijkstra_each.cpp` | 35 (زیرمسئله‌های ۳ و ۴) |
| `solution/sub2_vertex_weights.cpp` | 20 (زیرمسئله‌های ۱ و ۲) |
| `solution/floyd.cpp` | 15 (فقط زیرمسئله‌ی ۳) |
| `solution/sub1_equal_a.cpp` | 8 (فقط زیرمسئله‌ی ۱) |
| `solution/wrong_star_min_a.cpp` | 0 |
| `public/cpp/botfriends.cpp` (قالب خالی) | 0، ولی باید **بدون خطای کامپایل** باشد |

اگر نتیجه با جدول نخواند:

| علامت | علت احتمالی |
|---|---|
| همه‌ی ارسال‌ها Compilation failed | `grader.cpp` یا `botfriends.h` آپلود نشده، یا زبان C++ فعال نیست |
| همه‌ی تست‌ها ۰ با پیام checker | `checker` آپلود نشده یا Output evaluation روی comparator نیست |
| خطای «No testcase matches» یا امتیاز عجیب | تست‌ها کامل آپلود نشده‌اند یا پارامترهای GroupMin درست کپی نشده‌اند |
| تعداد تست کمتر از ۶۹ | الگوها `*.in` و `*.out` نبوده‌اند یا یکی از zipها آپلود نشده |
| امتیاز کل بر اساس آخرین ارسال است | Score mode روی گزینه‌ی IOI 2017- نیست |

**زمان‌ها را چک کنید.** در صفحه‌ی ارسال `model.cpp` در پنل، زمان هر تست نمایش داده می‌شود:
- روی ماشین من بیشترین زمان حدود ۰٫۵ ثانیه بود (محدودیت ۴ ثانیه است).
- اگر روی سرور بیشتر از حدود ۱٫۵ ثانیه شد، یا `floyd.cpp` زیرمسئله‌ی ۴ را گرفت، با من هماهنگ کنید تا محدودیت زمان بازبینی شود.
- برای عوض کردن زمان بعد از آزمون آزمایشی: dataset را **Clone** کنید، در نسخه‌ی کپی Time limit را عوض کنید و آن را **Activate** کنید.

---

## چک‌لیست نهایی

- [ ] Title و متن `fa` با تیک Primary
- [ ] پیوست `botfriends.zip`
- [ ] Score mode = IOI 2017-
- [ ] Time limit = 4، Memory limit = 512
- [ ] Batch، با grader، I/O خالی، comparator
- [ ] سه manager: `grader.cpp`، `botfriends.h`، `checker`
- [ ] ۶۹ تست
- [ ] GroupMin با پارامترهای `score_type_parameters.json`
- [ ] سوال به آزمون اضافه شده و فقط C++ فعال است
- [ ] ارسال آزمایشی `model.cpp` = ۱۰۰ و بقیه مطابق جدول گام ۸
