from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    x_fintrack_invoice_id = fields.Char(
        string="Fintrack Invoice ID",
        index=True,
        copy=False,
        help="UUID of the AP invoice in FINTRAC Control (GetDIST).",
    )
    x_fintrack_customer_invoice_id = fields.Char(
        string="Fintrack Customer Invoice ID",
        index=True,
        copy=False,
        help="UUID of the linked AR invoice row in FINTRAC Control (GetDIST).",
    )
    x_fintrack_factoring_case_id = fields.Char(
        string="Fintrack Factoring Case ID",
        index=True,
        copy=False,
        help="UUID of the factoring case in FINTRAC Control (GetDIST).",
    )
