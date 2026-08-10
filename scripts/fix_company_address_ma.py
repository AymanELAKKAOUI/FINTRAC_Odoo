"""Inspect and fix company address/country on fintrack_dev for l10n_ma."""
import json
import sys

company = env.company
partner = company.partner_id
morocco = env.ref("base.ma")
mad = env.ref("base.MAD")

before = {
    "company_id": company.id,
    "company_name": company.name,
    "country": partner.country_id.code if partner.country_id else None,
    "currency": company.currency_id.name if company.currency_id else None,
    "street": partner.street,
    "city": partner.city,
    "zip": partner.zip,
    "email": partner.email,
    "phone": partner.phone,
    "vat": partner.vat,
}

needs_fix = (
    not partner.country_id
    or partner.country_id.code != "MA"
    or not partner.street
    or not partner.city
)

if needs_fix:
    partner.write(
        {
            "street": partner.street or "Casablanca Finance City",
            "city": partner.city or "Casablanca",
            "zip": partner.zip or "20000",
            "country_id": morocco.id,
            "email": partner.email or "admin@fintrack.local",
            "phone": partner.phone or "+212 5 22 00 00 00",
        }
    )
    company.write(
        {
            "country_id": morocco.id,
            "currency_id": mad.id,
        }
    )
    env.cr.commit()
    print("Applied default Morocco company address.", file=sys.stderr)
else:
    print("Company address already set.", file=sys.stderr)

partner.invalidate_recordset()
company.invalidate_recordset()

after = {
    "company_id": company.id,
    "company_name": company.name,
    "country": partner.country_id.code if partner.country_id else None,
    "currency": company.currency_id.name if company.currency_id else None,
    "street": partner.street,
    "city": partner.city,
    "zip": partner.zip,
    "email": partner.email,
    "phone": partner.phone,
    "vat": partner.vat,
    "l10n_ma_installed": bool(
        env["ir.module.module"].search([("name", "=", "l10n_ma"), ("state", "=", "installed")], limit=1)
    ),
}

print(json.dumps({"before": before, "after": after}, indent=2, ensure_ascii=False))
