"""P0 UI validation: create vendor bill, pay from Bank and Cash, verify Fintrack fields."""
import json
import sys

from odoo import fields

partner = env["res.partner"].search([("supplier_rank", ">", 0)], limit=1)
if not partner:
    partner = env["res.partner"].create(
        {"name": "P0 UI Validation Vendor", "is_company": True, "supplier_rank": 1}
    )

tax20 = env["account.tax"].search(
    [("type_tax_use", "=", "purchase"), ("amount", "=", 20), ("company_id", "=", env.company.id)],
    limit=1,
)
bank_journal = env["account.journal"].search(
    [("type", "=", "bank"), ("company_id", "=", env.company.id)], limit=1
)
cash_journal = env["account.journal"].search(
    [("type", "=", "cash"), ("company_id", "=", env.company.id)], limit=1
)

move = env["account.move"].create(
    {
        "move_type": "in_invoice",
        "partner_id": partner.id,
        "invoice_date": fields.Date.today(),
        "ref": "P0-UI-VALIDATION",
        "x_fintrack_invoice_id": "00000000-0000-4000-8000-000000000001",
        "invoice_line_ids": [
            (
                0,
                0,
                {
                    "name": "P0 validation — office supplies",
                    "quantity": 1,
                    "price_unit": 1000.0,
                    "tax_ids": [(6, 0, tax20.ids)],
                },
            )
        ],
    }
)
move.action_post()

# Pay 600 from Bank
pay_bank = env["account.payment.register"].with_context(active_model="account.move", active_ids=move.ids).create(
    {
        "amount": 600.0,
        "journal_id": bank_journal.id,
        "payment_date": fields.Date.today(),
    }
)
pay_bank._create_payments()

move.invalidate_recordset()
remaining = move.amount_residual

# Pay remainder from Cash
if remaining > 0.01:
    pay_cash = env["account.payment.register"].with_context(
        active_model="account.move", active_ids=move.ids
    ).create(
        {
            "amount": remaining,
            "journal_id": cash_journal.id,
            "payment_date": fields.Date.today(),
        }
    )
    pay_cash._create_payments()

move.invalidate_recordset()

# Verify custom field readable
move_data = env["account.move"].search_read(
    [("id", "=", move.id)],
    ["id", "name", "ref", "amount_total", "amount_residual", "payment_state", "x_fintrack_invoice_id"],
)[0]

result = {
    "validation": "P0 UI equivalent",
    "database": env.cr.dbname,
    "vendor_bill": {
        "id": move_data["id"],
        "number": move_data["name"],
        "ref": move_data["ref"],
        "amount_total": move_data["amount_total"],
        "amount_residual": move_data["amount_residual"],
        "payment_state": move_data["payment_state"],
        "x_fintrack_invoice_id": move_data["x_fintrack_invoice_id"],
    },
    "bank_journal": {"id": bank_journal.id, "code": bank_journal.code},
    "cash_journal": {"id": cash_journal.id, "code": cash_journal.code},
    "fintrack_field_visible": move_data["x_fintrack_invoice_id"] == "00000000-0000-4000-8000-000000000001",
    "paid_from_bank_and_cash": move_data["payment_state"] in ("paid", "in_payment"),
    "ttc_ok": abs(move_data["amount_total"] - 1200.0) < 0.01,
}

env.cr.commit()
print(json.dumps(result, indent=2))
