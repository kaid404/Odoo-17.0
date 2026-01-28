from odoo import fields, models, api


class JuryMembersMarks(models.Model):
    _name = "jury.members.marks"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'jury_member_id'

    training_program_id = fields.Many2one('pixls.training.program', string="Training Program", store=True,
                                          tracking=True, )
    parameters_line_id = fields.Many2one('parameters.line', string="Parameter", store=True, tracking=True, )
    parameters_id = fields.Many2one('assignment.parameters', string="Parameter", store=True, tracking=True, )
    jury_member_id = fields.Many2one('hr.employee', string="Jury Member", store=True, tracking=True, domain=[('is_pixls_st', '=', False)])
    student_id = fields.Many2one('hr.employee', store=True, tracking=True, string="Student", domain=[('is_pixls_st', '=', True)])
    marks = fields.Float(string="Marks", store=True, tracking=True, )
    remarks = fields.Char(string="Remarks")
