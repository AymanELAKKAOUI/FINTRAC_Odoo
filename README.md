# Fintrack Odoo Services

Dockerized **Odoo 17** for FINTRAC Control (GetDIST) integration: supplier sync, CRM, and **accounting (Phase 0)**.

## Database naming

| Env | DB name | Notes |
|-----|---------|-------|
| **Local dev** | `fintrack_dev` | Used by GetDIST `.env` — **use this for integration** |
| Other | `FINTRAC` | Legacy/manual DB — do not point API here |

## Quick start

```bash
cd Odoo_services
docker compose up -d
```

Open **http://localhost:8069** and create a database (e.g. `fintrack_dev`).

## Install modules (baseline + Phase 0)

1. Go to **Apps** → **Update Apps List**
2. Install:
   - **Contacts**
   - **CRM**
   - **Purchase**
   - **Invoicing / Accounting** (`account`)
   - **Morocco - Accounting** (`l10n_ma`) — Option A localization
3. Install or upgrade **My Integration** v1.3.0+ (custom addon in `./addons/my_integration`)

The addon adds Fintrack fields on `res.partner`, `crm.lead`, `account.move`, `account.payment`, and `res.company`.

### Phase 0 setup scripts (CLI)

```powershell
cd Odoo_services
docker compose stop odoo
docker compose run --rm odoo odoo -d fintrack_dev -i account --stop-after-init
Get-Content scripts/setup_p0_ma.py | docker compose run --rm -T odoo odoo shell -d fintrack_dev --no-http
Get-Content scripts/ensure_ma_purchase_taxes.py | docker compose run --rm -T odoo odoo shell -d fintrack_dev --no-http
Get-Content scripts/verify_p0_accounting.py | docker compose run --rm -T odoo odoo shell -d fintrack_dev --no-http
docker compose up -d odoo
```

Registry IDs: `backend/GetDIST_project/docs/odoo-id-registry.dev.md`

## API user

1. **Settings → Users** → create `api_service_user`
2. Grant access to Contacts, CRM, Purchase, **Invoicing/Billing**, and **Accounting**
3. **Preferences → Account Security → API Keys** → generate a key

## Backend configuration

In `backend/GetDIST_project/.env`:

```env
ODOO_ENABLED=true
ODOO_BASE_URL=http://localhost:8069
ODOO_DB=fintrack_dev
ODOO_USERNAME=api_service_user
ODOO_API_KEY=your-api-key
```

Run migrations:

```bash
cd backend/GetDIST_project
npm run db:migrate
```

Test connection:

```bash
npm run test:odoo
npm run test:odoo-p0
```

## Sync suppliers (Fintrack → Odoo)

Each sync creates or updates:

| Fintrack | Odoo |
|----------|------|
| `finance.suppliers` | `res.partner` (vendor contact) |
| supplier profile | `crm.lead` (CRM opportunity) |

### CLI

```bash
npm run test:odoo-sync -- <company-uuid>
npm run test:odoo-sync -- <company-uuid> <supplier-uuid>
```

### API

| Method | Path | Permission |
|--------|------|------------|
| GET | `/api/integrations/odoo/status` | `supplier.view` |
| GET | `/api/integrations/odoo/suppliers` | `supplier.view` |
| POST | `/api/integrations/odoo/suppliers/sync` | `supplier.manage` |
| GET | `/api/integrations/odoo/partners` | `supplier.view` |

Sync body: `{}` for all suppliers, or `{ "supplierId": "<uuid>" }` for one.

### Frontend

On the **Suppliers** page (when Odoo is enabled):

- **Sync all to Odoo** — bulk sync
- Row menu → **Sync to Odoo** — single supplier
- **Odoo** column shows sync status

## View in Odoo

After sync:

- **Contacts** → synced vendors (`supplier_rank = 1`)
- **CRM → Pipeline** → opportunities named `Supplier — {name}`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ODOO_DISABLED` | Set `ODOO_ENABLED=true` in `.env` |
| Connection refused | `docker compose up -d` in `Odoo_services` |
| Missing custom fields | Upgrade **My Integration** addon |
| Auth failed | Regenerate API key; check username and database name |

## Repository layout

```
Odoo_services/
├── docker-compose.yml    # Postgres 15 + Odoo 17
├── addons/
│   └── my_integration/   # Fintrack integration addon
└── README.md
```
