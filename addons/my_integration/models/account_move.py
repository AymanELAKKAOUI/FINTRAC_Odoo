from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    x_fintrack_invoice_id = fields.Char(
        string="Fintrack Invoice ID",
        index=True,
        copy=False,
        help="UUID of the AP invoice in FINTRAC Control (GetDIST).",
    )
