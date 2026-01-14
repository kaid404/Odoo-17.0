from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpExamAttendees(models.Model):
    _name = "op.exam.attendees"
    _rec_name = "student_id"
    _description = "Exam Attendees"

    student_id = fields.Many2one('op.student', 'Student', required=True)
    status = fields.Selection(
        [('present', 'Present'), ('absent', 'Absent')],
        'Status', default="present", required=True)
    marks = fields.Integer('Marks')
    note = fields.Text('Note')
    exam_id = fields.Many2one(
        'op.exam', 'Exam', required=True, ondelete="cascade")
    course_id = fields.Many2one('op.course', 'Course', readonly=True)
    batch_id = fields.Many2one('op.batch', 'Batch', readonly=True)
    room_id = fields.Many2one('op.exam.room', 'Room')

    _sql_constraints = [
        ('unique_attendees',
         'unique(student_id,exam_id)',
         'Attendee must be unique per exam.'),
    ]

    class_name = fields.Many2one('op.academic.year', 'Class', required=False, compute='_compute_session_details',
                                 store=True, tracking=True)
    year_name = fields.Many2one('op.academic.term', 'Year', required=False, compute='_compute_session_details',
                                store=True, tracking=True)
    section_name = fields.Many2one('class.section', 'Section', required=False, compute='_compute_session_details',
                                   store=True, tracking=True)

    @api.depends('exam_id')
    def _compute_session_details(self):
        for record in self:
            if record.exam_id:
                record.class_name = record.exam_id.class_name.id
                record.year_name = record.exam_id.year_name.id
                record.section_name = record.exam_id.section_name.id
            else:
                record.class_name = False
                record.year_name = False
                record.section_name = False

    @api.onchange('exam_id')
    def onchange_exam(self):
        self.course_id = self.exam_id.session_id.course_id
        self.batch_id = self.exam_id.session_id.batch_id
        self.student_id = False

    @api.constrains('marks')
    def _check_marks(self):
        if self.marks < 0.0:
            raise ValidationError(_("Enter proper marks!"))
