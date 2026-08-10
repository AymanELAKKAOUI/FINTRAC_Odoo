"""Phase 0 setup: Morocco company, accounting ACLs, registry export.

Run:
  Get-Content scripts/setup_p0_ma.py | docker compose run --rm -T odoo odoo shell -d fintrack_dev --no-http
"""
import json
import sys

LOGIN = "api_service_user"
COMPANY = env.company

# --- P0-T2: Morocco company (Option A — l10n_ma) ---
if COMPANY.country_id.code != "MA":
    morocco = env.ref("base.ma")
    COMPANY.write(
        {
            "country_id": morocco.id,
            "currency_id": env.ref("base.MAD").id,
        }
    )
    print("Set company country=MA currency=MAD", file=sys.stderr)

# Ensure l10n_ma is installed
module = env["ir.module.module"].search([("name", "=", "l10n_ma")], limit=1)
if module and module.state != "installed":
    module.button_immediate_install()
    print("Installed l10n_ma", file=sys.stderr)
elif module:
    print("l10n_ma already installed", file=sys.stderr)
else:
    print("WARNING: l10n_ma module not found", file=sys.stderr)

env.cr.commit()

# --- P0-T6: API user accounting rights ---
user = env["res.users"].search([("login", "=", LOGIN)], limit=1)
if not user:
    raise SystemExit(f"User {LOGIN} not found")

group_ids = []
group_xmlids = [
    "base.group_user",
    "account.group_account_invoice",
    "account.group_account_user",
    "purchase.group_purchase_user",
    "sales_team.group_sale_salesman",
]
for xmlid in group_xmlids:
    group = env.ref(xmlid, raise_if_not_found=False)
    if group:
        group_ids.append(group.id)

if group_ids:
    user.write({"groups_id": [(6, 0, list(set(group_ids)))]})
    print(f"Granted {len(group_ids)} groups to {LOGIN}", file=sys.stderr)

env.cr.commit()

# --- P0-T8: Collect registry ---
journals = env["account.journal"].search([])
taxes = env["account.tax"].search([("type_tax_use", "=", "purchase")])

def pick_journal(jtype):
    matches = journals.filtered(lambda j: j.type == jtype)
    return matches[:1]

bank = pick_journal("bank")
cash = pick_journal("cash")

def pick_tax(rate):
    matches = taxes.filtered(lambda t: abs(t.amount - rate) < 0.001)
    return matches[:1]

registry = {
    "database": env.cr.dbname,
    "company": {
        "id": COMPANY.id,
        "name": COMPANY.name,
        "country": COMPANY.country_id.code,
        "currency": COMPANY.currency_id.name,
    },
    "journals": {
        "bank": {"id": bank.id, "code": bank.code, "name": bank.name} if bank else None,
        "cash": {"id": cash.id, "code": cash.code, "name": cash.name} if cash else None,
        "all": [{"id": j.id, "code": j.code, "name": j.name, "type": j.type} for j in journals],
    },
    "purchase_taxes": [
        {"id": t.id, "name": t.name, "amount": t.amount}
        for t in taxes.sorted(key=lambda x: x.amount, reverse=True)
    ],
    "purchase_tax_by_rate": {
        "20": {"id": pick_tax(20).id, "name": pick_tax(20).name} if pick_tax(20) else None,
        "14": {"id": pick_tax(14).id, "name": pick_tax(14).name} if pick_tax(14) else None,
        "10": {"id": pick_tax(10).id, "name": pick_tax(10).name} if pick_tax(10) else None,
        "7": {"id": pick_tax(7).id, "name": pick_tax(7).name} if pick_tax(7) else None,
        "0": {"id": pick_tax(0).id, "name": pick_tax(0).name} if pick_tax(0) else None,
    },
    "api_user": {
        "id": user.id,
        "login": user.login,
        "groups": [g.full_name for g in user.groups_id],
    },
    "accounting_installed": bool(
        env["ir.module.module"].search([("name", "=", "account"), ("state", "=", "installed")], limit=1)
    ),
    "l10n_ma_installed": bool(
        env["ir.module.module"].search([("name", "=", "l10n_ma"), ("state", "=", "installed")], limit=1)
    ),
}

print(json.dumps(registry, indent=2, ensure_ascii=False))
