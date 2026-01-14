from odoo import models, fields


class OpCourse(models.Model):
    _inherit = "op.course"

    fees_term_id = fields.Many2one('op.fees.terms', 'Fees Term')
