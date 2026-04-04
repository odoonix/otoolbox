# Copilot Instructions Guideline (Extensible)

هدف این سند: یک چارچوب قابل توسعه برای نگهداری `copilot-instructions` در سطح workspace و repo.

## 1) هدف و دامنه
- این guideline مشخص می‌کند `copilot-instructions` چطور نوشته، تقسیم، و بازبینی شوند.
- دامنه:
  - `/.github/copilot-instructions.md` (سطح workspace)
  - `**/.copilot-instructions.md` (سطح repo)
  - `docs/*.md` (اسناد موضوعی)

## 2) معماری پیشنهادی
- فایل مرکزی (`/.github/copilot-instructions.md`) باید کوتاه بماند و شامل:
  - Topic Map
  - قواعد سراسری
  - قاعده precedence
- اسناد موضوعی در `docs/` باید domain-specific باشند (هر فایل یک موضوع)
- فایل repo-local برای قواعد خاص همان ریپو است و باید بر قواعد کلی override داشته باشد.

## 3) Rule Precedence (خیلی مهم)
1. Repo-local rule (نزدیک‌ترین `.copilot-instructions.md`)
2. Workspace-level rule (`/.github/copilot-instructions.md`)
3. Topic docs (`docs/*.md`)

در تعارض، همیشه rule مشخص‌تر برنده است.

## 4) استاندارد کیفیت برای هر Rule
هر rule باید این ویژگی‌ها را داشته باشد:
- **Actionable:** قابل اجرا و غیرمبهم
- **Scoped:** دقیقاً مشخص کند کجا اعمال می‌شود
- **Testable:** بشود بررسی کرد رعایت شده یا نه
- **Minimal:** بدون تکرار یا توضیح اضافی

## 5) الگوی نگارش پیشنهاد‌شده
برای هر rule از الگوی زیر استفاده کنید:

- **Rule:** چه کاری باید انجام شود
- **Why:** دلیل فنی/سازمانی
- **Do:** نمونه صحیح
- **Don’t:** ضدالگو

نمونه:
- Rule: تغییرات business logic را در `odoonix/*` یا `oca/*` انجام بده.
- Why: جلوگیری از fork drift روی upstream.
- Do: افزودن inherited model در addon هدف.
- Don’t: patch مستقیم `odoo/odoo` بدون نیاز صریح.

## 6) ضدالگوهای رایج (برای حذف)
- قوانین متناقض زبانی (مثلاً همزمان الزام به English و Persian rewrite)
- قوانین مطلق غیرواقعی (`MUST` برای فایل‌هایی که همیشه لازم نیست مثل `constants.py`)
- لینک/ارجاع به فایل‌هایی که وجود ندارند
- متن طولانی بدون Topic Map

## 7) سیاست زبان
- زبان اصلی قواعد: English (برای سازگاری ابزارها و تیم‌های چندزبانه)
- توضیح تیمی/آموزشی می‌تواند فارسی هم باشد.
- از ruleهای متناقض درباره ترجمه خودکار پرهیز شود.

## 8) سیاست نسخه‌گذاری و تغییرات
- هر تغییر مهم در قواعد باید در PR با عنوان مشخص ثبت شود.
- برای تغییرات policy:
  - why
  - affected repos
  - migration note (اگر لازم)
- پیشنهاد: بخش `Changelog` انتهای هر guideline مهم.

## 9) Review Checklist (برای maintainers)
- [ ] آیا rule جدید actionable است؟
- [ ] آیا با ruleهای قبلی conflict ندارد؟
- [ ] آیا scope آن مشخص است (workspace/repo/topic)؟
- [ ] آیا مثال Do/Don’t دارد؟
- [ ] آیا لینک‌ها و مسیرها معتبرند؟

## 10) Template برای اسناد topic جدید
```md
# <Topic Title>

## Purpose
<what this file controls>

## Rules
- <rule 1>
- <rule 2>

## Do
- <good example>

## Don’t
- <bad example>

## Validation
- <how to verify compliance>
```

## 11) پیشنهاد عملی برای این workspace
- Topic map را همیشه با فایل‌های واقعی `docs/` sync نگه دارید.
- قواعد OCA را در `docs/05-oca-contributing-reference.md` نگه دارید.
- قواعد repo-specific (مثلاً connector) را فقط در `.copilot-instructions.md` همان repo قرار دهید.
