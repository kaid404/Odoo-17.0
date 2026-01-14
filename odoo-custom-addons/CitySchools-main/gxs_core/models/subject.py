from odoo import models, fields, api, _


class OpSubject(models.Model):
    _name = "op.subject"
    _inherit = "mail.thread"
    _description = "Subject"

    name = fields.Char('Name', size=128, required=True)
    code = fields.Char('Code', size=256, required=True)
    class_id = fields.Many2one('op.academic.year', string='Class')
    grade_weightage = fields.Float('Grade Weightage')
    type = fields.Selection(
        [('theory', 'Theory'), ('practical', 'Practical'),
         ('both', 'Both'), ('other', 'Other')],
        'Type', default="theory", required=True)
    subject_type = fields.Selection(
        [('compulsory', 'Compulsory'), ('elective', 'Elective')],
        'Subject Type', default="compulsory", required=True)
    department_id = fields.Many2one(
        'op.department', 'Department',
        default=lambda self:
        self.env.user.dept_id and self.env.user.dept_id.id or False)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_subject_code',
         'unique(code)', 'Code should be unique per subject!'),
    ]

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Subjects'),
            'template': '/gxs_core/static/xls/op_subject.xls'
        }]
