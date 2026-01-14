from pkg_resources import require

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpResultTemplate(models.Model):
    _name = "op.result.template"
    _inherit = ["mail.thread"]
    _description = "Result Template"

    exam_session_id = fields.Many2one(
        'op.exam.session', 'Exam Session',
        required=True, tracking=True)
    evaluation_type = fields.Selection(
        related='exam_session_id.evaluation_type',
        store=True, tracking=True)
    name = fields.Char("Name", size=254,
                       required=True, tracking=True)
    result_date = fields.Date(
        'Result Date', required=True,
        default=fields.Date.today(), tracking=True)
    grade_ids = fields.Many2many(
        'op.grade.configuration', string='Grade Configuration',required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('result_generated', 'Result Generated')
    ], string='State', default='draft', tracking=True)
    active = fields.Boolean(default=True)

    class_name = fields.Many2one('op.academic.year', 'Class', required=False, compute='_compute_session_details',
                                 store=True, tracking=True)
    year_name = fields.Many2one('op.academic.term', 'Year', required=False, compute='_compute_session_details',
                                store=True, tracking=True)
    section_name = fields.Many2one('class.section', 'Section', required=False, compute='_compute_session_details',
                                   store=True, tracking=True)

    @api.depends('exam_session_id')
    def _compute_session_details(self):
        for record in self:
            if record.exam_session_id or 1==1:
                record.class_name = record.exam_session_id.class_name.id
                record.year_name = record.exam_session_id.year_name.id
                record.section_name = record.exam_session_id.section_name.id
            else:
                record.class_name = False
                record.year_name = False
                record.section_name = False

    @api.constrains('exam_session_id')
    def _check_exam_session(self):
        for record in self:
            for exam in record.exam_session_id.exam_ids:
                if exam.state != 'done':
                    raise ValidationError(
                        _('All subject exam should be done.'))

    @api.constrains('grade_ids')
    def _check_min_max_per(self):
        for record in self:
            count = 0
            for grade in record.grade_ids:
                for sub_grade in record.grade_ids:
                    if grade != sub_grade:
                        if (sub_grade.min_per <= grade.min_per and
                            sub_grade.max_per >= grade.min_per) or \
                                (sub_grade.min_per <= grade.max_per and
                                 sub_grade.max_per >= grade.max_per):
                            count += 1
            if count > 0:
                raise ValidationError(
                    _('Percentage range conflict with other record.'))

    def generate_result(self):
        for record in self:
            marksheet_reg_id = self.env['op.marksheet.register'].create({
                'name': 'Mark Sheet for %s' % record.exam_session_id.name,
                'exam_session_id': record.exam_session_id.id,
                'generated_date': fields.Date.today(),
                'generated_by': self.env.uid,
                'state': 'draft',
                'result_template_id': record.id
            })
            student_dict = {}
            for exam in record.exam_session_id.exam_ids:
                for attendee in exam.attendees_line:
                    result_line_id = self.env['op.result.line'].create({
                        'student_id': attendee.student_id.id,
                        'exam_id': exam.id,
                        'marks': str(attendee.marks and attendee.marks or 0),
                    })
                    if attendee.student_id.id not in student_dict:
                        student_dict[attendee.student_id.id] = []
                    student_dict[attendee.student_id.id].append(result_line_id)
            for student in student_dict:
                marksheet_line_id = self.env['op.marksheet.line'].create({
                    'student_id': student,
                    'marksheet_reg_id': marksheet_reg_id.id,
                })
                for result_line in student_dict[student]:
                    result_line.marksheet_line_id = marksheet_line_id
            record.state = 'result_generated'
