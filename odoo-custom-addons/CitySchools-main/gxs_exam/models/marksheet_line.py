from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpMarksheetLine(models.Model):
    _name = "op.marksheet.line"
    _rec_name = "student_id"
    _description = "Marksheet Line"

    marksheet_reg_id = fields.Many2one(
        'op.marksheet.register', 'Marksheet Register')
    evaluation_type = fields.Selection(
        related='marksheet_reg_id.exam_session_id.evaluation_type',
        store=True)
    student_id = fields.Many2one('op.student', 'Student', required=True)
    result_line = fields.One2many(
        'op.result.line', 'marksheet_line_id', 'Results')
    total_marks = fields.Integer("Total Marks",
                                 compute='_compute_total_marks',
                                 store=True)
    percentage = fields.Float("Percentage", compute='_compute_percentage',
                              store=True)
    recieved = fields.Boolean(string='Recieved By Parent', store=True)
    remarks = fields.Char(string='Remarks', store=True)
    generated_date = fields.Date(
        'Generated Date', required=True,
        default=fields.Date.today())
    grade = fields.Char('Grade', readonly=True, compute='_compute_grade',store=True)

    class_id = fields.Many2one('op.academic.year',related='marksheet_reg_id.exam_session_id.course_id.class_id', string='Class', store=True, copy=True)

    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')
    ], 'Status', compute='_compute_status', store=True)
    active = fields.Boolean(default=True)

    class_name = fields.Many2one('op.academic.year', 'Class', readonly=True, compute='_compute_session_details',
                                 required=False, tracking=True)
    year_name = fields.Many2one('op.academic.term', 'Year', required=True, readonly=False,
                                compute='_compute_session_details', tracking=True)
    section_name = fields.Many2one('class.section', 'Section', required=True, readonly=False,
                                   compute='_compute_session_details', tracking=True)

    @api.depends('marksheet_reg_id')
    def _compute_session_details(self):
        for record in self:
            if record.marksheet_reg_id or 1==1:
                record.class_name = record.marksheet_reg_id.class_name.id
                record.year_name = record.marksheet_reg_id.year_name.id
                record.section_name = record.marksheet_reg_id.section_name.id
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

    @api.constrains('total_marks', 'percentage')
    def _check_marks(self):
        for record in self:
            if (record.total_marks < 0.0) or (record.percentage < 0.0):
                raise ValidationError(_("Enter proper marks or percentage!"))

    @api.depends('result_line.marks')
    def _compute_total_marks(self):
        for record in self:
            record.total_marks = sum([
                int(x.marks) for x in record.result_line])

    @api.depends('total_marks')
    def _compute_percentage(self):
        for record in self:
            total_exam_marks = sum(
                [int(x.exam_id.total_marks) for x in record.result_line])
            record.percentage = \
                record.total_marks and \
                (100 * record.total_marks) / total_exam_marks or 0.0

    @api.depends('percentage')
    def _compute_grade(self):
        for record in self:
            record.evaluation_type = 'grade'
            if record.evaluation_type == 'grade':
                grades = record.marksheet_reg_id.result_template_id.grade_ids
                for grade in grades:
                    if grade.min_per <= record.percentage and \
                            grade.max_per >= record.percentage:
                        record.grade = grade.result
                        break
                    else:
                        record.grade = None
            else:
                record.grade = None

    @api.depends('result_line.status')
    def _compute_status(self):
        for record in self:
            record.status = 'pass'
            for result in record.result_line:
                if result.status == 'fail':
                    record.status = 'fail'
