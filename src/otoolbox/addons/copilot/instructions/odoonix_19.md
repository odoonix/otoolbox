

Code style

Better using self.env._ More info at https://github.com/odoo/odoo/pull/174844



Performance

W8163(no-search-all), Using an empty domain `search([])` without a `limit` will load all records, may impact performance.

W8113(attribute-string-redundant), ResCompany The attribute string is redundant. String parameter equal to name of variable
