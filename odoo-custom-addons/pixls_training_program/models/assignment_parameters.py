from odoo import fields, models, api


class AssignmentParameters(models.Model):
    _name = "assignment.parameters"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', store=True)
    training_program_id = fields.Many2one('pixls.training.program', string='Training Program',required=True)
    total = fields.Float(string="Total")

