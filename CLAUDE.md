# CLAUDE.md — ریپوی سوال‌های آزمون هفتگی دوره‌ی طلا

این ریپو سوال‌های OI-style را با TPS نگه می‌دارد. سوال نمونه‌ی کامل و تأییدشده: `lice/`. ساختار و سطح کیفیت آن را الگو قرار بده.

## محیط و قراردادها (تکرار نکن، از همین‌ها استفاده کن)
- TPS: submodule در `tps/` (ioi-2017/tps @ fd2b587، اسکریپت‌ها 1.25). اگر خالی بود: `git submodule update --init`؛ نصب: `cd tps && sudo ./install-tps.sh` + `psutil`، `dos2unix`.
- سوال جدید:
  1. `tps init <name> -T "$PWD/tps/task-templates" -t default -D ...` (پارامترها را با `-D` بده؛ لیستشان در `tps/task-templates/default/task-template-instantiate.sh`).
  2. بعد `scripts` را symlink به `../tps/scripts` کن و `testlib.h` در gen/validator/checker را symlink به `../../common/testlib.h`.
  3. `statement/assets` و فایل‌های HTML قالب را پاک کن.
- grader: برای جلوگیری از جعل خروجی `has_output_secret=true`؛ grader کل ورودی را بخواند، `stdin` را ببندد، بعد تابع را صدا بزند.
- validator: یک هدر مشترک (مثل `lice/validator/tree_input.h`) + یک validator جدا برای هر زیرمسئله.
- gen: یک مولد پارامتری testlib با seed از آرگومان؛ در `gen/data` با `@subtask`/`@include` شمول زیرمسئله‌ها را بساز، هر تست یک بار.
- checker: testlib، کامل‌خواندن خروجی، همه‌ی خطاهای خواندن ⇒ WA، و تست‌های دست‌ساز در `checker/tests/` با `run.sh`.
  - ترتیب آرگومان checker در TPS/CMS: `input judge_answer contestant_output`.
  - مسیر `checker/tests/*.out` در `.gitignore` سوال باید از ignore خارج شود.
- متن: `statement/index.md` فارسی + PDF با `node tools/statement/build.js statement/index.md statement/<name>-fa.pdf` (یک بار `npm install` در `tools/statement`).
- کدها سبک cp؛ grader و checker خوانا و امن.

## CMS (درس‌های گرفته‌شده)
- کاربر **فقط دسترسی پنل ادمین CMS** دارد (نه شل). نسخه‌ی هدف: CMS 1.5.1.
- خروجی: `tps export CMS 1` (protocol 2 با loader رسمی CMS کار نمی‌کند).
- بسته‌ی آپلود دستی:
  - `python3 ../tools/make_cms_upload.py statement/<name>-fa.pdf` (داخل پوشه‌ی سوال، بعد از `tps gen`)؛
  - خروجی: checker کامپایل‌شده‌ی static (gnu++14)، zip تست‌ها زیر ۱۰۰MB، پارامترهای GroupMin با regex لنگردار، و `SETTINGS.md`.
- تنظیمات دستی در CMS 1.5.1:
  - Score mode = IOI 2017- (`max_subtask`)؛ loader 1.5.1 این را نمی‌گذارد؛
  - primary statement = `fa`.
- راهنماها: `docs/cms-admin-only-fa.md` (فقط پنل)، `docs/cms-guide-fa.md` (نصب کامل).

## کیفیت (لازم قبل از اعلام اتمام)
- راه‌حل اصلی + یک راه‌حل درست مستقل + راه‌حل هر زیرمسئله + راه‌حل‌های غلط/کند رایج، با حکم دقیق در `solutions.json`؛ `tps invoke` همه باید «match with expected» باشند.
- stress با brute روی n کوچک (و `tps stress`)؛ هر ادعای درستی بدون اثبات کامل را صریح بگو.
- زمان راه‌حل اصلی روی بدترین تست ≥ ۲–۳ برابر کمتر از TL؛ راه‌حل‌های کند با فاصله رد شوند.
  - اگر راه‌حل هدف یک زیرمسئله نزدیک TL است، قید را کم کن.
  - شمول تست‌ها (مثلاً ΣN) را بعد از تغییر قید چک کن.
- validator ⇔ متن: هر قید در هر دو.
- بعد از هر مرحله‌ی مهم commit و push روی شاخه‌ی کاری (نه main).
- خلاصه‌ی نهایی کوتاه: نوع، ایده، زیرمسئله‌ها، محدودیت‌ها، checker، جدول invoke، و مراحل آپلود در CMS.
