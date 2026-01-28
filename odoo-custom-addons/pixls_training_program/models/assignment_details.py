from odoo import fields, models, api


class AssignmentDetails(models.Model):
    _name = "assignment.details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'assignment_id'

    training_program_id = fields.Many2one('pixls.training.program', string="Training Program", store=True, )
    training_assignment_line_id = fields.Many2one('pixls.training.assignment.line', string="Training Assignment Lines")
    assignment_details_lines = fields.One2many('assignment.details.line', 'assignment_details_id',
                                               string="Assignment Details Lines")
    week = fields.Selection([('week_1', 'Week 1'), ('week_2', 'Week 2')], store=True, string='Week', required=True)
    assignment_id = fields.Many2one('assignment.data', string='Assignment', required=True, store=True, )
    total_marks = fields.Float(string="Total Marks")
    weightage = fields.Float(string='Weightage', store=True, related='assignment_id.weightage')


class AssignmentDetailsLines(models.Model):
    _name = 'assignment.details.line'
    _description = 'Training Student Line'

    assignment_details_id = fields.Many2one('assignment.details', string='Assignment Details Id', ondelete='cascade')
    student_id = fields.Many2one('hr.employee', string='Student', required=True, domain=[('is_pixls_st', '=', True)])
    marks = fields.Float(string="Marks")
    total_marks = fields.Float(string="Total Marks")
    remarks = fields.Char(string="Remarks")
    percentage = fields.Float(
        string="Percentage",
        compute="_compute_percentage",
        store=True
    )
    weightage = fields.Float(string='Weightage', store=True, compute="_compute_percentage", )

    @api.depends('marks', 'total_marks')
    def _compute_percentage(self):
        for rec in self:
            if rec.total_marks:
                rec.percentage = (rec.marks / rec.total_marks)
                rec.weightage = (((rec.marks / rec.total_marks) * 100) * rec.assignment_details_id.weightage) / 100

                student_lines = rec.assignment_details_id.training_program_id.students
                for st in student_lines:
                    st.total_weight_percentage()

            else:
                rec.percentage = 0
                rec.rec.weightage = 0
