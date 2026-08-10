"""Create Morocco purchase VAT taxes for GetDIST rates (20/14/10/7/0) if missing."""
import json
import sys

COMPANY = env.company
rates = [20.0, 14.0, 10.0, 7.0, 0.0]
Tax = env["account.tax"]
Account = env["account.account"]

# Try to find a deductible VAT account from l10n_ma chart
vat_account = Account.search(
    [
        ("company_id", "=", COMPANY.id),
        ("account_type", "in", ["asset_current", "liability_current"]),
        ("name", "ilike", "tax"),
    ],
    limit=1,
)
if not vat_account:
    vat_account = Account.search(
        [("company_id", "=", COMPANY.id), ("code", "like", "345%")],
        limit=1,
    )

created = []
for rate in rates:
    existing = Tax.search(
        [
            ("type_tax_use", "=", "purchase"),
            ("amount", "=", rate),
            ("company_id", "=", COMPANY.id),
        ],
        limit=1,
    )
    if existing:
        continue

    name = f"VAT {rate:g}% P"
    values = {
        "name": name,
        "amount": rate,
        "amount_type": "percent",
        "type_tax_use": "purchase",
        "company_id": COMPANY.id,
    }
    if vat_account:
        values["invoice_repartition_line_ids"] = [
            (0, 0, {"repartition_type": "base", "factor_percent": 100}),
            (
                0,
                0,
                {
                    "repartition_type": "tax",
                    "factor_percent": 100,
                    "account_id": vat_account.id,
                },
            ),
        ]
        values["refund_repartition_line_ids"] = [
            (0, 0, {"repartition_type": "base", "factor_percent": 100}),
            (
                0,
                0,
                {
                    "repartition_type": "tax",
                    "factor_percent": 100,
                    "account_id": vat_account.id,
                },
            ),
        ]

    tax = Tax.create(values)
    created.append({"id": tax.id, "name": tax.name, "amount": tax.amount})

env.cr.commit()
print(json.dumps({"created": created, "vat_account_id": vat_account.id if vat_account else None}, indent=2))
