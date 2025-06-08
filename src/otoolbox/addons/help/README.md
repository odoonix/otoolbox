# Otoolbox Addon: Help

To update db on server

```bash
db=DataBaseName
/var/lib/odoo/odoo-bin -c /etc/odoo/odoo.conf  -d $db -u all --without-demo=all --no-http --stop-after-init
```

برای اینکه تمام دسترسی‌های دیگه به پایگاه داده بسته بشه.

```slq
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'demo17'
  AND pid <> pg_backend_pid();
```
