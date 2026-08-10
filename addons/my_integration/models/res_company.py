from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    x_fintrack_company_id = fields.Char(
        string="Fintrack Company ID",
        copy=False,
        help="UUID of the company in FINTRAC Control (GetDIST).",
    )
