from odoo import models, fields


class OpFacilityLine(models.Model):
    _inherit = "op.facility.line"

    classroom_id = fields.Many2one('op.classroom', 'Classroom')
