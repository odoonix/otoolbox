# Odoo Patterns (Odoo 19)

## Preferred Module Boundaries
- Business features should go into `odoonix/*` or `oca/*` first.
- Avoid editing `odoo/odoo` unless explicitly required.
- Keep model/view/security/data changes inside the target addon.

## Addon Structure
- Standard layout: `__manifest__.py`, `models/`, `views/`, `security/`, optional `controllers/` and `tests/`.
- Keep dependencies and metadata accurate in each addon manifest.

## Connector Guidance
- Reuse patterns from sibling connectors before creating abstractions.
- Primary connector areas:
  - `odoonix/connector/*`
  - `oca/connector/*`
- Common families: `connector_base`, `connector_shopify`, `connector_xero`, `connector_wordpress`.

## Localization/Translation API
- In Odoo 19 code, prefer `self.env._(...)` in model methods.
