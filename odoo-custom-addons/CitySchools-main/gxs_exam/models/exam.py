import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpStudent(models.Model):
    _inherit = "op.student"

    def get_exam(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Result',
            'view_mode': 'tree,form',
            'res_model': 'op.marksheet.line',
            'domain': [('student_id', '=', self.id)],
            # 'target': 'current',
        }

class OpExam(models.Model):
    _name = "op.exam"
    _inherit = "mail.thread"
    _description = "Exam"

    session_id = fields.Many2one('op.exam.session', 'Exam Session',
                                 domain=[('state', 'not in',
                                          ['cancel', 'done'])])
    course_id = fields.Many2one(
        'op.course', related='session_id.course_id', store=True,
        readonly=True)
    batch_id = fields.Many2one(
        'op.batch', 'Batch', related='session_id.batch_id', store=True,
        readonly=True)
    subject_id = fields.Many2one('op.subject', 'Subject', required=True)
    exam_code = fields.Char('Exam Code', size=16, required=False, copy=False)
    attendees_line = fields.One2many(
        'op.exam.attendees', 'exam_id', 'Attendees', readonly=True)
    start_time = fields.Datetime('Start Time', required=True)
    end_time = fields.Datetime('End Time', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('schedule', 'Scheduled'), ('held', 'Held'),
         ('result_updated', 'Result Updated'),
         ('cancel', 'Cancelled'), ('done', 'Done')], 'State',
        readonly=True, default='draft', tracking=True)
    note = fields.Text('Note')
    responsible_id = fields.Many2many('op.faculty', string='Responsible')
    name = fields.Char('Exam', size=256, required=False, copy=False)
    total_marks = fields.Integer('Total Marks', required=True)
    min_marks = fields.Integer('Passing Marks', required=True)
    active = fields.Boolean(default=True)

    class_name = fields.Many2one('op.academic.year', 'Class', required=False, compute='_compute_session_details',
                                 store=True, tracking=True)
    year_name = fields.Many2one('op.academic.term', 'Year', required=False, compute='_compute_session_details',
                                store=True, tracking=True)
    section_name = fields.Many2one('class.section', 'Section', required=False, compute='_compute_session_details',
                                   store=True, tracking=True)

    @api.depends('session_id')
    def _compute_session_details(self):
        for record in self or 1==1:
            if record.session_id:
                record.class_name = record.session_id.class_name.id
                record.year_name = record.session_id.year_name.id
                record.section_name = record.session_id.section_name.id
            else:
                record.class_name = False
                record.year_name = False
                record.section_name = False

    _sql_constraints = [
        ('unique_exam_code',
         'unique(exam_code)', 'Code should be unique per exam!')]

    @api.constrains('total_marks', 'min_marks')
    def _check_marks(self):
        if self.total_marks <= 0.0 or self.min_marks <= 0.0:
            raise ValidationError(_('Enter proper marks!'))
        if self.min_marks > self.total_marks:
            raise ValidationError(_(
                "Passing Marks can't be greater than Total Marks"))

    @api.constrains('start_time', 'end_time')
    def _check_date_time(self):
        session_start = datetime.datetime.combine(
            fields.Date.from_string(self.session_id.start_date),
            datetime.time.min)
        session_end = datetime.datetime.combine(
            fields.Date.from_string(self.session_id.end_date),
            datetime.time.max)
        start_time = fields.Datetime.from_string(self.start_time)
        end_time = fields.Datetime.from_string(self.end_time)
        if start_time > end_time:
            raise ValidationError(_('End Time cannot be set before Start Time.'))
        elif start_time < session_start or start_time > session_end or \
                end_time < session_start or end_time > session_end:
            raise ValidationError(
                _('Exam Time should in between Exam Session Dates.'))

    def act_result_updated(self):
        self.state = 'result_updated'

    def act_done(self):
        self.state = 'done'

    def act_draft(self):
        self.state = 'draft'

    def act_cancel(self):
        self.state = 'cancel'

    @api.onchange('session_id', 'subject_id')
    def _onchange_session_subject(self):
        # Check if both session_id and subject_id are selected
        if self.session_id and self.subject_id:
            # Combine session name and subject name
            self.name = f"{self.session_id.name} - {self.subject_id.name}"
            self.exam_code = f"{self.session_id.exam_code} - {self.subject_id.code}"
        else:
            self.name = False
            self.exam_code = False
