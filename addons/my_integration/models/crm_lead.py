from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    x_fintrack_supplier_id = fields.Char(
        string="Fintrack Supplier ID",
        index=True,
        copy=False,
        help="UUID of the supplier in FINTRAC Control (GetDIST).",
    )
