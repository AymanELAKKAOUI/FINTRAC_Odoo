from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    x_fintrack_payment_id = fields.Char(
        string="Fintrack Payment ID",
        index=True,
        copy=False,
        help="UUID of the payment in FINTRAC Control (GetDIST).",
    )
