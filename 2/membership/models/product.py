from odoo import api, fields, models
from dateutil.relativedelta import relativedelta  # Add this import

class Product(models.Model):
    _inherit = 'product.template'

    membership = fields.Boolean(help='Check if the product is eligible for membership.')
    membership_duration = fields.Selection(
        selection=[
            ('3', '3 Months'),
            ('6', '6 Months'),
            ('12', '12 Months'),
        ],
        string='Membership Duration',
        help="Membership duration from purchase date."
    )
    membership_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Paid Member Pricelist',
        help="Pricelist for active paid members."
    )
    non_member_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Non-Member Pricelist',
        help="Pricelist for non-members, free members, or expired members.",
        required=True  # Mandatory field
    )

