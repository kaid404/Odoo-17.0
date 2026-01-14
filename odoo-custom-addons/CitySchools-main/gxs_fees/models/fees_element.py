from odoo import models, fields


class OpFeesElementLine(models.Model):
    _name = "op.fees.element"
    _description = "Fees Element for course"

    sequence = fields.Integer('Sequence')
    product_id = fields.Many2one('product.product',
                                 'Product(s)', required=True)
    value = fields.Float('Value (%)')
    fees_terms_line_id = fields.Many2one('op.fees.terms.line',
                                         string='Fees Terms')
