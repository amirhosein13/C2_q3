# سوال‌های آزمون هفتگی (TPS)

هر سوال یک پوشه‌ی TPS مستقل است، با `scripts/` کپی‌شده‌ی خودش. TPS به‌صورت submodule در `tps/` قرار دارد و روی کامیت `fd2b587` (اسکریپت‌ها نسخه‌ی 1.25) ثابت شده است.

## راه‌اندازی

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

قراردادها و درس‌های کار با این ریپو در `CLAUDE.md` است. راهنمای آپلود فقط از پنل ادمین در `docs/cms-admin-only-fa.md` است.

ساخت PDF متن سوال به `node` و Playwright (Chromium) نیاز دارد. یک بار در `tools/statement` این را بزنید:

```bash
npm install
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
```bash
node ../tools/statement/build.js statement/index.md statement/<task>-fa.pdf
```
```bash
python3 ../tools/make_cms_upload.py statement/<task>-fa.pdf
```
```bash
tps export CMS 1
```

`tps invoke` محدودیت حافظه را اعمال نمی‌کند. برای راه‌حل‌هایی که حافظه‌ی زیادی می‌گیرند، قبلش این را بزنید:

```bash
ulimit -v 1500000
```

## وارد کردن در CMS

پروتکل ۱ با loader `tps_task` در همه‌ی نسخه‌های CMS اصلی (1.4 به بعد) سازگار است. فایل zip را روی سرور باز کنید و این دستور را بزنید:

```bash
cmsImportTask -L tps_task <task-dir>
```

PDF متن سوال جدا (از پنل ادمین) به سوال اضافه می‌شود، چون exporter آن را در بسته نمی‌گذارد.

**مهم:** loader در CMS 1.5.x (و قبل‌تر) حالت امتیازدهی را تنظیم نمی‌کند و پیش‌فرض `max_tokened_last` می‌ماند. بعد از import در پنل ادمین، Score mode سوال را روی `max_subtask` (بهترین امتیاز هر زیرمسئله، به سبک IOI) بگذارید. نسخه‌ی master خودش `max_subtask` می‌گذارد.

import با CMS 1.5.1 محلی (PostgreSQL 16) تست شده است. داوری واقعی (Worker و isolate) روی سرور تست نشده و زمان‌ها باید روی خود سرور دوباره چک شوند.

## سوال‌ها

| پوشه | عنوان | نوع |
|---|---|---|
| `botfriends/` | دوستان ربات | Batch با grader |
