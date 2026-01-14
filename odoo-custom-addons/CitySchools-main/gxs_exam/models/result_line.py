from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpResultLine(models.Model):
    _name = "op.result.line"
    _rec_name = "marks"
    _description = "Result Line"

    marksheet_line_id = fields.Many2one(
        'op.marksheet.line', 'Marksheet Line', ondelete='cascade')
    exam_id = fields.Many2one('op.exam', 'Exam', required=True)
    evaluation_type = fields.Selection(
        related='exam_id.session_id.evaluation_type', store=True)
    marks = fields.Integer('Marks', required=True)
    grade = fields.Char('Grade', readonly=True, compute='_compute_grade',store=True)
    student_id = fields.Many2one('op.student', 'Student', required=True)
    status = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], 'Status',
                              compute='_compute_status', store=True)

    subject_id = fields.Many2one('op.subject', 'Subject',related="exam_id.subject_id", required=False)

    class_name = fields.Many2one('op.academic.year', 'Class', required=False, compute='_compute_session_details',
                                 store=True, tracking=True)
    year_name = fields.Many2one('op.academic.term', 'Year', required=False, store=True,
                                compute='_compute_session_details'
                                , tracking=True)
    section_name = fields.Many2one('class.section', 'Section', required=False,
                                   store=True, compute='_compute_session_details'
                                   , tracking=True)

    @api.depends('exam_id')
    def _compute_session_details(self):
        for record in self:
            if record.exam_id or 1==1:
                record.class_name = record.exam_id.class_name.id
                record.year_name = record.exam_id.year_name.id
                record.section_name = record.exam_id.section_name.id
            else:
                record.class_name = False
                record.year_name = False
                record.section_name = False

    # class_name = fields.Many2one(
    #     'op.academic.year', 'Class',
    #     required=True, tracking=True)
    # year_name = fields.Many2one(
    #     'op.academic.term', 'Year',
    #     required=True, tracking=True)
    # section_name = fields.Many2one(
    #     'class.section', 'Section',
    #     required=True, tracking=True)

    @api.constrains('marks', 'marks')
    def _check_marks(self):
        for record in self:
            if record.marks < 0.0:
                raise ValidationError(_("Enter proper Marks or Percentage!"))

    @api.depends('marks')
    def _compute_grade(self):
        for record in self:
            if record.evaluation_type == 'grade':
                grades = record.marksheet_line_id.marksheet_reg_id. \
                    result_template_id.grade_ids
                if grades:
                    for grade in grades:
                        if grade.min_per <= record.marks and \
                                grade.max_per >= record.marks:
                            record.grade = grade.result
                else:
                    record.grade = None
            else:
                record.grade = None

    @api.depends('marks')
    def _compute_status(self):
        for record in self:
            record.status = 'pass'
            if record.marks < record.exam_id.min_marks:
                record.status = 'fail'
            else:
                record.status = 'pass'

    def unlink(self):
        for res in self:
            super(OpResultLine, res).unlink()
        return self
