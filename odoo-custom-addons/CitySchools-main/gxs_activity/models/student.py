from odoo import models, fields


class OpStudent(models.Model):
    _inherit = "op.student"

    activity_log = fields.One2many('op.activity', 'student_id',
                                   string='Activity Log')
    activity_count = fields.Integer(compute='compute_count')

    def get_activity(self):
        action = self.env.ref('gxs_activity.'
                              'act_open_op_activity_view').read()[0]
        action['domain'] = [('student_id', 'in', self.ids)]
        return action

    def compute_count(self):
        for record in self:
            record.activity_count = self.env['op.activity'].search_count(
                [('student_id', 'in', self.ids)])
