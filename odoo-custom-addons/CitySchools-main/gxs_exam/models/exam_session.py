from pkg_resources import require

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpExamSession(models.Model):
    _name = "op.exam.session"
    _inherit = ["mail.thread"]
    _description = "Exam Session"

    name = fields.Char(
        'Exam Session', size=256, required=True, tracking=True)
    course_id = fields.Many2one(
        'op.course', 'Course', required=True, tracking=True)
    batch_id = fields.Many2one(
        'op.batch', 'Batch', required=False, tracking=True)
    exam_code = fields.Char(
        'Exam Session Code', size=16,
        required=True, tracking=True)
    start_date = fields.Date(
        'Start Date', required=True, tracking=True)
    end_date = fields.Date(
        'End Date', required=True, tracking=True)
    exam_ids = fields.One2many(
        'op.exam', 'session_id', 'Exam(s)')
    exam_type = fields.Many2one(
        'op.exam.type', 'Exam Type',
        required=True, tracking=True)
    evaluation_type = fields.Selection(
        [('normal', 'Normal'), ('grade', 'Grade')],
        'Evaluation type', default="normal",
        required=True, tracking=True)
    venue = fields.Many2one(
        'res.partner', 'Venue', tracking=False,required=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('schedule', 'Scheduled'),
        ('held', 'Held'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
    ], 'State', default='draft', tracking=True)
    active = fields.Boolean(default=True)

    class_name = fields.Many2one('op.academic.year', 'Class', required=True, tracking=True)
    year_name = fields.Many2one('op.academic.term', 'Year', required=True, tracking=True)
    section_name = fields.Many2one('class.section', 'Section', required=True, tracking=True)

    _sql_constraints = [
        ('unique_exam_session_code',
         'unique(exam_code)', 'Code should be unique per exam session!')]

    @api.constrains('start_date', 'end_date')
    def _check_date_time(self):
        if self.start_date > self.end_date:
            raise ValidationError(
                _('End Date cannot be set before Start Date.'))

    @api.onchange('course_id')
    def onchange_course(self):
        self.batch_id = False

    def act_draft(self):
        self.state = 'draft'

    def act_schedule(self):
        self.state = 'schedule'

    def act_held(self):
        self.state = 'held'

    def act_done(self):
        self.state = 'done'

    def act_cancel(self):
        self.state = 'cancel'
