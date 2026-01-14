from odoo import models, fields, api


class OpAttendanceSheet(models.Model):
    _name = "op.attendance.sheet"
    _inherit = ["mail.thread"]
    _description = "Attendance Sheet"
    _order = "attendance_date desc"

    name = fields.Char('Name', readonly=True, size=32)
    register_id = fields.Many2one(
        'op.attendance.register', 'Register', required=True,
        tracking=True)
    course_id = fields.Many2one(
        'op.course', related='register_id.course_id', store=True,
        readonly=True)
    batch_id = fields.Many2one(
        'op.batch', 'Batch', related='register_id.batch_id', store=True,
        readonly=True)
    session_id = fields.Many2one('op.session', 'Session')
    attendance_date = fields.Date(
        'Date', required=True, default=lambda self: fields.Date.today(),
        tracking=True)
    attendance_line = fields.One2many(
        'op.attendance.line', 'attendance_id', 'Attendance Line')
    faculty_id = fields.Many2one('op.faculty', 'Faculty')
    section_name = fields.Char(string='Section')
    class_name = fields.Char(string='Class')
    year = fields.Char(string='Year')
    active = fields.Boolean(default=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('start', 'Attendance Start'),
         ('done', 'Attendance Taken'), ('cancel', 'Cancelled')],
        'Status', default='draft', tracking=True)
    # faculty_id

    def attendance_draft(self):
        self.state = 'draft'

    def attendance_start(self):
        self.state = 'start'

    def attendance_done(self):
        student_course = self.env['op.student.course'].search([('course_id','=',self.register_id.course_id)])
        for rec in student_course:
            rec._compute_att_line_ids()
            rec.compute_attendance_percentage()
        self.state = 'done'

    def attendance_cancel(self):
        self.state = 'cancel'

    _sql_constraints = [
        ('unique_register_sheet',
         'unique(register_id,session_id,attendance_date)',
         'Sheet must be unique per Register/Session.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sheet = self.env['ir.sequence'].next_by_code('op.attendance.sheet')
            register = self.env['op.attendance.register']. \
                browse(vals['register_id']).code
            vals['name'] = register + sheet
        return super(OpAttendanceSheet, self).create(vals_list)
