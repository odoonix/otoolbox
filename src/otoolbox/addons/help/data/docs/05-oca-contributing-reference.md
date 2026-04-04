# OCA Contributing Reference (Copilot + Team)

> Based on OCA contributing guide:
> `https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst`
>
> هدف این سند: تبدیل راهنمای طولانی OCA به یک مرجع اجرایی کوتاه برای توسعه‌دهنده‌ها و Copilot.

## 1) اصول پایه
- کیفیت کد باید به خوانایی، نگهداری‌پذیری، پایداری، و کاهش regression کمک کند.
- تغییرات باید **generic** باشند (قابل استفاده توسط جامعه)، نه company-specific hardcode.
- هر bugfix بهتر است همراه unittest باشد.

## 2) ساختار ماژول OCA
- ساختار استاندارد addon را رعایت کنید: `__manifest__.py`, `models/`, `views/`, `security/`, `tests/`, ...
- فایل‌ها را بر اساس مدل تقسیم کنید (یک فایل برای هر مدل یا inherited model).
- نام فایل‌ها و شناسه‌ها با الگوی واضح و قابل جستجو باشد.
- `README.rst` در بسیاری از پروژه‌های OCA از `readme/*` تولید می‌شود؛ مستقیم و بی‌دلیل دستکاری نشود.

## 3) قواعد مهم `__manifest__.py`
- کلیدهای خالی نگذارید.
- لایسنس باید مشخص باشد.
- وابستگی‌ها دقیق و حداقلی باشند.
- برای external dependency از `external_dependencies` استفاده شود.
- در نسخه‌گذاری از الگوی OCA/Odoo branch + semver module استفاده شود (مثل `19.0.x.y.z`).

## 4) XML Guidelines (فشرده)
- تورفتگی 4-space.
- رکوردها را تا حد ممکن بر اساس مدل گروه‌بندی کنید.
- نام `xml_id`ها قابل پیش‌بینی و استاندارد باشد.
- از `replace` در inheritance فقط در صورت ضرورت واقعی و با توضیح واضح استفاده شود.
- Demo record xmlidها با پسوند `demo` قابل تشخیص باشند.

## 5) Python Guidelines (فشرده)
- ترتیب importها: stdlib → third-party → odoo → local.
- PEP8 + readability-first.
- نام‌گذاری معنادار و snake_case.
- الگوهای متد Odoo رعایت شود (`_compute_*`, `_onchange_*`, `action_*`, ...).
- از ORM استفاده کنید؛ bypass غیرضروری DB ممنوع.
- SQL امن: پارامتری، بدون string interpolation.
- `cr.commit()`/`cr.rollback()` دستی داخل flow معمول RPC/test انجام ندهید.

## 6) Tests: ضد-Flaky
- تست را deterministic بنویسید (تاریخ ثابت، عدم اتکا به زمان جاری).
- به سرویس خارجی واقعی در تست unit/integration عادی وصل نشوید؛ mock کنید.
- روی demo data تکیه نکنید؛ داده تست را خودتان بسازید.
- تست را با حداقل دسترسی لازم هم پوشش دهید تا false positive کمتر شود.

## 7) Git/PR Rules
- یک تغییر منطقی = یک commit منطقی.
- پیام commit کوتاه، روشن، انگلیسی، imperative mood.
- PR باید دلیل تغییر، رفتار قبل/بعد، و روش تست را شفاف بگوید.
- تغییرات cross-module را بی‌دلیل در یک PR قاطی نکنید.

## 8) Review Culture
- review باید فنی + محترمانه + قابل اقدام باشد.
- روی این موارد حساس باشید:
  - نبود تست کافی
  - طراحی ضعیف یا non-generic
  - ناسازگاری با conventions OCA
  - مشکلات license/authorship

## 9) Translation Rule
- در OCA معمولاً `.po` ها با Weblate مدیریت می‌شوند.
- در PRهای معمول، تغییر دستی `.po` را تا حد ممکن انجام ندهید مگر سناریوی مجاز پروژه.

## 10) Migration & Breaking Changes
- برای breaking change، مسیر migration را مستندسازی کنید.
- در صورت نیاز، migration script اضافه شود.
- تغییرات ناسازگار را واضح در README/notes توضیح دهید.

## 11) Quick Checklist Before PR
- [ ] ماژول ساختار استاندارد OCA را دارد.
- [ ] `__manifest__.py` کامل، بدون کلید خالی، با license/dependencies صحیح.
- [ ] naming فایل/مدل/xmlid استاندارد و قابل جستجوست.
- [ ] تست مرتبط اضافه/به‌روزرسانی شده و پایدار است.
- [ ] SQL ناامن، bypass ORM، commit/rollback دستی وجود ندارد.
- [ ] توضیح PR شفاف است (why + what + how tested).

## 12) Copilot Usage Prompts (Ready to Copy)
- `Follow docs/05-oca-contributing-reference.md and docs/02-odoo-patterns.md for this addon change.`
- `Apply OCA-style file naming, manifest hygiene, and deterministic tests.`
- `Review this diff against OCA rules: XML IDs, ORM usage, test quality, and commit readiness.`

## 13) Notes for This Workspace
- این workspace ترکیبی از `odoo/`, `oca/`, `odoonix/`, `moonsunsoft/` است.
- اولویت توسعه business feature در `odoonix/*` یا `oca/*` است مگر نیاز صریح به upstream.
- از این سند به‌عنوان **مرجع یادگیری تیم** + **راهنمای اجرای Copilot** استفاده کنید.
