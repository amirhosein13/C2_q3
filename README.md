# سوال‌های آزمون هفتگی (TPS)

هر سوال یک پوشه‌ی TPS مستقل است، با `scripts/` کپی‌شده‌ی خودش.
TPS به‌صورت submodule در `tps/` قرار دارد و روی کامیت `fd2b587` (اسکریپت‌ها نسخه‌ی 1.25) ثابت شده است.

## راه‌اندازی

اگر پوشه‌ی `tps/` خالی است:

```bash
git submodule update --init
```
```bash
cd tps && sudo ./install-tps.sh
```
```bash
pip install psutil
```
```bash
sudo apt install dos2unix
```

برای ساخت PDF متن این‌ها لازم است: `pandoc`، `node` با بسته‌ی `playwright` (و Chromium آن)، و فونت Vazirmatn. فونت با این دستور نصب می‌شود:

```bash
sudo apt install fonts-vazirmatn
```

## دستورهای اصلی (داخل پوشه‌ی سوال)

```bash
tps gen
```
```bash
tps invoke solution/model.cpp
```
```bash
tps verify
```

`tps invoke` محدودیت حافظه را اعمال نمی‌کند. برای راه‌حل‌هایی که حافظه‌ی زیاد می‌گیرند، قبلش این را بزنید:

```bash
ulimit -v 1500000
```

## ابزارها (`tools/`)

| ابزار | کار |
|---|---|
| `statement-pdf/build.sh <md> <pdf>` | PDF فارسی راست‌به‌چپ از متن Markdown؛ فرمول‌ها با MathML و چاپ با Chromium |
| `cms_upload.py [pdf]` | بسته‌ی آپلود دستی از پنل ادمین CMS 1.5.1 را در `<task>/cms-upload/` می‌سازد؛ داخل پوشه‌ی سوال و بعد از `tps gen` اجرا شود |
| `cms_loader_check.py <cms> <export> <cms-upload>` | loader رسمی `tps_task` یک checkout از CMS را بدون پایگاه داده اجرا و با بسته مقایسه می‌کند |
| `cms_aws_upload_test.py <url> <user> <pass> <cms-upload> <task>` | بسته را از فرم‌های AdminWebServer یک CMS **آزمایشی** آپلود می‌کند |
| `cms_grade_emulation.py <cms-upload> <task> <sol.cpp>...` | داوری Batch با grader و checker و GroupMin را فقط با فایل‌های بسته شبیه‌سازی می‌کند |

## سوال‌ها

| پوشه | عنوان | نوع |
|---|---|---|
| `botfriends/` | دوستان ربات | Batch با grader |

راهنمای گام‌به‌گام آپلود این سوال در CMS: [`botfriends/UPLOAD-GUIDE-fa.md`](botfriends/UPLOAD-GUIDE-fa.md)
