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

ساخت PDF متن سوال به `pandoc`، `node` با `playwright` و فونت Vazirmatn نیاز دارد. فونت با این دستور نصب می‌شود:

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
```bash
statement/build_pdf.sh
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

## سوال‌ها

| پوشه | عنوان | نوع |
|---|---|---|
| `botfriends/` | دوستان ربات | Batch با grader |
