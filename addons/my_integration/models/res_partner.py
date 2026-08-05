from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_fintrack_supplier_id = fields.Char(
        string="Fintrack Supplier ID",
        index=True,
        copy=False,
        help="UUID of the supplier in FINTRAC Control (GetDIST).",
    )
    x_fintrack_company_id = fields.Char(
        string="Fintrack Company ID",
        copy=False,
        help="UUID of the owning company in FINTRAC Control.",
    )
