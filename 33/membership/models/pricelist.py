# pricelist.py (new file)
from odoo import fields, models

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    is_membership_pricelist = fields.Boolean(
        string='For Memberships',
        help="Designates this pricelist for membership customers."
    )