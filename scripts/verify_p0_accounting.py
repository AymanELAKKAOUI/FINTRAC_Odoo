"""Verify accounting ACL: create draft vendor bill with 20% tax via API user context."""
import json
import sys

from odoo import fields

LOGIN = "api_service_user"
user = env["res.users"].search([("login", "=", LOGIN)], limit=1)
if not user:
    raise SystemExit(f"User {LOGIN} not found")

partner = env["res.partner"].search([("supplier_rank", ">", 0)], limit=1)
if not partner:
    partner = env["res.partner"].create(
        {
            "name": "P0 Test Vendor",
            "is_company": True,
            "supplier_rank": 1,
        }
    )

tax = env["account.tax"].search(
    [
        ("type_tax_use", "=", "purchase"),
        ("amount", "=", 20),
        ("company_id", "=", env.company.id),
    ],
    limit=1,
)
if not tax:
    tax = env["account.tax"].search(
        [
            ("type_tax_use", "=", "purchase"),
            ("name", "ilike", "20%"),
            ("company_id", "=", env.company.id),
        ],
        limit=1,
    )
if not tax:
    tax = env["account.tax"].search(
        [("type_tax_use", "=", "purchase"), ("company_id", "=", env.company.id)],
        limit=1,
    )

UserEnv = env(user=user)
move = UserEnv["account.move"].create(
    {
        "move_type": "in_invoice",
        "partner_id": partner.id,
        "invoice_date": fields.Date.today(),
        "invoice_line_ids": [
            (
                0,
                0,
                {
                    "name": "P0 ACL test line",
                    "quantity": 1,
                    "price_unit": 1000.0,
                    "tax_ids": [(6, 0, tax.ids)] if tax else [],
                },
            )
        ],
    }
)

result = {
    "move_id": move.id,
    "partner_id": partner.id,
    "amount_untaxed": move.amount_untaxed,
    "amount_tax": move.amount_tax,
    "amount_total": move.amount_total,
    "state": move.state,
    "tax_used": {"id": tax.id, "name": tax.name, "amount": tax.amount} if tax else None,
    "expected_total": 1200.0 if tax and abs(tax.amount - 20) < 0.001 else None,
    "ttc_ok": abs(move.amount_total - 1200.0) < 0.01 if tax and abs(tax.amount - 20) < 0.001 else None,
}

# Roll back test bill — P0 verification only
env.cr.rollback()
print(json.dumps(result, indent=2))
