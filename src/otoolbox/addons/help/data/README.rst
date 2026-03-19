.. ODOONIX-AUTO-GENERATED-CONTENT-BEGIN
.. THIS PART OF THE HELP IS GENERATED AUTOMATICALY, DONOT UPDAT

Odoonix Toolbox
================

زمانی که می‌خواهید یک پروژه اودوو انجام دهید و یا اینکه برای مشتریانی اودوو را نگهداری
کنید با تعداد نسخه‌های متفاوت روبرو هستید. یا تعداد ماژولها و مخزن‌های متفاوتی وجود دارد.

کنترل این ماژولها بسیار زمانبر است. برای همین ما فرآیندهای متفاوت را به شکل ابزارهایی
ایجاد کردیم.
این فرآیندها شامل به روز رسانی، تست، دنبال کردن وضعیت ماژولها و یا سایر فرآیندهای دیگر
است. این ابزارها به شکل دستورات خط فرمان هستند که می‌توانید آنها را اجرا کنید و نتیجه را ببینید.
این ابزارها به شما کمک می‌کنند که کارهای تکراری را به شکل خودکار
انجام دهید و در وقت خود صرفه جویی کنید. همچنین این ابزارها به شما کمک می‌کنند که خطاها را سریعتر کشف کنید و آنها را حل کنید.
در این بخش از راهنما، ما به شما نشان خواهیم داد که چگونه از این ابزارها استفاده کنید و چگونه آنها را در پروژه‌های خود به کار ببرید.


Repositories and Folder structure
---------------------------------------------------------------------------------------------

تمام این ابزارها برای یک سازمان طراحی شده که می‌خواهد مشتری‌های متفاوتی در اودوو را
مدیریت کند.

در این شرکت‌ها ما دو دسته کد و مخزن نرم افزاری داریم که باید مدیریت کنیم.
تمام این مخزن‌ها شامل افزونه‌های اودوو است.
این مخزن‌ها عبارتند از:

- مخزن‌های کد مشتری
- مخزن‌های کد 3rd parties

Customer Repositories
++++++++++++++++++++++++++++++++++++++++++++

یک پوشه باید وجود داشته باشه و تمام مشتری‌ها در آن ایجاد و مدیریت شوند.
معمولا ما نام Customers  را برای آن در نظر می‌گیریم.

در سطح اول برای هر مشتری باید یک پوشه باشد. نام این پوشه معادل با  نام ارگانیزیشن
است که متعلق به مشتری است.

در مرحله دوم مخزن گیت وجود دارد که متعلق به مشتری است و تمام کدهای مشتری در آن قرار
می‌گیرد.

بعضی از مشتری‌ها چندین اودوو دارند و هر اودوو چند ماژول دارد.

در هر مخزن مشتری یک فایل به نام moonsun.env وجود دارد که اطلاعات مشتری در آن به صورت
یک لیست متغیر و مقدار نمایش داده می‌شود.

برای نمونه در یک پروژه:

.. code-block:: bash

    CUSTOMER_NAME="Moonsun PTL. LTD."
    CUSTOMER_VERSION="18.0"
    CUSTOMER_BRANCH_PRODUCTION="main"
    CUSTOMER_BRANCH_STAGING="staging"
    ...

این فایل برای هر مشتری به صورت مستقل تولید و به روز می‌شود.
در هر مخزن مشتری باید این فایل باشد. بر اساس اطالعات این فایل بسیاری از پردازش‌ها
انجام می‌شود.


معمولا هیچ ماژولی به صورت مستقیم در مخزن‌های مشتری توسعه و نگهداری داده نمی‌شود.
برای همین یک فایل به نام .gitmodules وجود دارد که فهرست مخزن‌های لینک شده
به مخزن مشتری را نشان می‌دهد.

این ساختار تقریبا ساختاری است که برای مدیریت ماژول‌های شرکت‌های متفاوت برای نمونه:

.. code-blok:: bash

    [submodule "OCA/stock-logistics-warehouse"]
            path = OCA/stock-logistics-warehouse
            url = git@github.com:OCA/stock-logistics-warehouse.git
            branch = 17.0

    [submodule "OCA/stock-logistics-workflow"]
            path = OCA/stock-logistics-workflow
            url = git@github.com:OCA/stock-logistics-workflow.git
            branch = 17.0


ساختاری که برای مدیریت ماژولها در نظر گرفته شده به صورت زیر است

.. code-blok:: bash

    Organization/Repository


ممکن است که مخزن‌های متفاوتی به مشتری لینک شده باشد.

3rd Party repositories
++++++++++++++++++++++++++++++++++++++++++++

یک پوشه جداگانه برای مدیریت ماژولهایی در نظر می‌گیریم که یا ما توسعه می‌دهیم
یا توسط شرکت‌های دیگر توسعه داده می‌شوند.
معمولا ما از عنوان Projects برای آن استفاده می‌کنیم.


ما مشتری‌های متفاوتی داریم و یا حتی برای یک مشتری ممکن است نسخه‌های متفاوتی
از اودوو داشته باشیم.
در سطح اول برای هر نسخه از اودوو یک پوشه ایجاد می‌کنیم که ماژولها را در ان
توسعه داده و نگهداری کنیم.

هر نسخه مثل یک workspase عمل می‌کند که تنظیم‌های مربوط برای محیط توسعه در ان
ذخیره می‌شود.
در هر workspace فهرستی از فایلهای پیکره بندی وجود دارد که عبارتند از:


- .copilot-instructions.md : copilot configuration of workspace
- .env                     : environtment settings & otoolbox setting
- odoo-dev.code-workspace  : worksapce config
- odools.toml              : confiuration for odoo extension of VS Code
- README.md                : document for the worksapce
- repositoires.json        : list of repositories
- requirements.txt         : required python libs 
- .tmp                     : a folder for temprory files

فایل .evn خیلی مهم است. تنظیمات otoolbox هست که مدیریت کلی ماژولهایی که توسعه
داده می‌شوند را انجام می‌دهد

نمونه‌ای از این فایل:

.. code-block::bash

    AUTHOR="Odoonix"
    EMAIL="info@odoonix.com"
    WEBSITE="https://odoonix.com"
    GITHUB="https://githubs.com/odoonix"
    VENV_PATH=".venv"
    ODOO_VERSION="19.0"
    SILENT="False"
    PRE_CHECK="False"
    POST_CHECK="False"
    VERIFY="False"
    CONTINUE_ON_EXCEPTION="True"
    SSH_AUTH="True"
    PUBLIC_ORGANIZATION="odoonix"
    SHIELDED_ORGANIZATION="moonsunsoft"
    WORKER_USER="worker"
    CUSTOMER_ROOT_DIR="/path/to/folder/Customers"

این فایلها زمان پیکره بندی workspace ایجاد شده و در طول زمان به روز رسانی و
مدیریت می‌شود.

معمولا در پروژه‌های بزرگ با شرکت‌های متفاوتی کار خواهیم کرد.
بنابر این بدیهی است که با تعداد مخزن‌های متفاوتی روبرو باشیم که هر کدام شامل
ماژولهای متفاوتی هستند.
بنابر این باید ساختاری را برای مدیریت ماژولها در نظر بگیریدم

یک پوشه برای شرکت و Organization وجود دارد که تمام مخزن‌هایی که از ان
شرکت هست را مدیریت می‌کند.

فهرست زیر Organization هایی است که به صورت پیش فرض مدیریت می‌شوند.

- odoo
- oca
- moonsunsoft
- odoonix



Best practies
++++++++++++++++++++++++++++++++++++++++++++

بهترین ساختار برای مدیریت کارها به صورت زیر است. 


.. code-block:: bash

    ├── 17.0
    │   ├── moonsunsoft
    │   ├── oca
    │   ├── odoo
    │   ├── odoo-dev.code-workspace
    │   ├── odools.toml
    │   ├── odoonix
    │   ├── README.md
    │   ├── .env
    │   ├── repositoires.json
    │   └── requirements.txt
    ├── 18.0
    │   ├── moonsunsoft
    │   ├── oca
    │   ├── odoo
    │   ├── odoo-dev.code-workspace
    │   ├── odools.toml
    │   ├── odoonix
    │   ├── README.md
    │   ├── .env
    │   ├── repositoires.json
    │   └── requirements.txt
    ├── 19.0
    │   ├── moonsunsoft
    │   ├── oca
    │   ├── odoo
    │   ├── odoo-dev.code-workspace
    │   ├── odools.toml
    │   ├── odoonix
    │   ├── README.md
    │   ├── .env
    │   ├── repositoires.json
    │   └── requirements.txt
    ├── Customers
        ├── Moonsun
        └── My




Tools and Utilites
---------------------------------------------------------------------------------------------

در حالت کلی دو دسته ابزار برای کار ایجاد شده. ابزارهای پایه و اسکریپت‌هایی که فرآیندها
سازمان را اجرا می‌کنند.

این دسته بندی بر اساس نیازهای ما در مدیریت توسعه و مدیریت نسخه‌های مشتری ایجاد شده است.

Base Tools
+++++++++++++

این ابزارها کارهای عمومی برای انواع پروژه‌ها انجام می‌دهند.

- git
- otoolbox
- nano
- vscode

مهم‌ترین آنها otoolbox هست.

دستور زیر را اجرا کنید که راهنمای به روز این ابزار را مشاهده کنید:

.. code-block::bash

    $ otoolbox --help


برای نمونه نصب و به روز کردن اسکریپت‌های اوبونتو به سورت زیر است


.. code-block:: bash

    pipx install otoolbox

    pipx upgrade otoolbox

    otoolbox --help

    otoolbox run init

    otoolbox run update --tags git

    otooblox run update --tags ubuntu

    otoolbox run update --tags odoo-dev.code-workspace

    otoolbox repo add oca/server-tools



Automation scripts
+++++++++++++++++++

دو دسته اسکریپت آماده شده

- To manage repositories
- To manage customers

قبل از اینکه این اسکریپت‌ها را بررسی کنیم حتما باید ساختار مخزن‌های کد رو بررسی
کنید. تمام این اسکریپت‌ها بر اساس ساختارهای پیاده‌ای طراحی شده که در بخش قبل
توضیح داده شده است.

این اسکریپت‌ها برای انجام کارهای روزمره ایجاد شده و تنها در پروژه‌های اودوو کاربرد دارد.

این دستورها در .venv نصب و اضافه می‌شوند.

برای استفاده از انها حتما باید یک venv فعال داشته باشید مثلا

.. code-block:: bash

    source Projects/19.0/.venv/bin/activate

با این کار این دستورها فعال شده و قابل استفاده هستند.


Repository management
***********************

ساختار کلی این دستورها به صورت زیر است

.. code-block:: bash

    ls bulk-*

برای نمونه به روز کردن تمام مخزن‌ها نرم افزاری

.. code-block:: bash

    bulk-pull

    bulk-push


Customer management
************************


ساختار کلی این دستورها به صورت زیر است

.. code-block:: bash

    ls customer-*

برای نمونه به روز کردن تمام مخزن‌ها نرم افزاری

.. code-block:: bash

    customer-init

    customer-info

    customer-update-submodule



Logs and Trubleshooting
---------------------------------------------------------------------------------------------

تمام ابزارهایی که استفاده می‌کنیم در خط فرمان لاگ تولید می‌کنند تا بتوانید
مشکلات را پیدا و حل کنید.


علاوه بر این لاگ‌ها در فایل‌هایی جمع اوری می‌کنند.
هر دستوری که اجرا می‌شود لاگهایش در سیستم ذخیره می‌شود. از این لاگ‌ها برای کشف خطا و بررسی
حالت سیستم استفاده می‌شود.
نسخه جاری امکان کشف خطای خودکار ندارد. در صورتی که خطایی رخ دهد کار به درستی انجام
نمی‌شود. هیچ نشانه‌ای هم وجود ندارد که شما تشخیص دهی که کار به درستی انجام نشده.
تنها راه ممکن خواندن لاگها است. بهترین روش این هست که لاگهای سیستم را بعد از هر اجرای
دستور بخوانید.

لاگها در مسیر زیر بر اساس نام دستوری که اجرا می‌کنید و تاریخ اجرا ذخیره می‌شوند:

.. code-block::bash

    .tmp/{commmand name}-{date}.log


برای نمونه اگر شما دستور زیر را اجرا کنید:

.. code-block::bash

    $ bulk-pull

آنگاه یک لاگ به نام زیر و در مسیر زیر ایجاد می‌شود:

.. code-block::bash

    .tmp/bulk-pull-2026-05-24.log

از انجا که دستورات متفاوتی برای انجام کارها استفاده می‌شود تنها راه درست برای فهمیدن
درست اجرا شدن دستورها بررسی لاگ است. در متن لاگ نوع خطا و روش حل آن نیز وجود دارد.




.. ODOONIX-AUTO-GENERATED-CONTENT-END


