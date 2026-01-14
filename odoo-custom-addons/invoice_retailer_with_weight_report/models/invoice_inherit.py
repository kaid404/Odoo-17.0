from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_weight = fields.Float(
        string='Weight',
        related='product_id.weight',
        store=True,
        readonly=True
    )
