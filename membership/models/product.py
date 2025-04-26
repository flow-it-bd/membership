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
        string='Membership Pricelist',
        help="Pricelist applied to members during their active membership period."
    )

    # Remove the old fields and SQL constraint
    # membership_date_from = fields.Date(...)
    # membership_date_to = fields.Date(...)
    # _sql_constraints = [...]
