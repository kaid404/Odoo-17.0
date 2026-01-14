from odoo import models,fields,api

class StudentCourseInherit(models.Model):
    _inherit = 'op.student.course'

    att_line_ids = fields.Many2many('op.attendance.line', 'attendance_line_student_rel', 'student_id', 'attendance_line_id', string="Attendance Lines",  store=True)
    attendance_percentage = fields.Float('Attendance %',store=True)

    # @api.depends('att_line_ids')
    def _compute_att_line_ids(self):
        for student in self:
            attendance_lines = self.env['op.attendance.line'].search([('student_id','=',student.student_id.id),
                                                                             ('attendance_id.course_id.class_id','=',
                                                                              student.student_id.year_id.id),
                                                                             ('attendance_id.state','=','done')])
            student.att_line_ids = attendance_lines

    # @api.depends('att_line_ids')
    def compute_attendance_percentage(self):
        for rec in self:
            attendance_lines = self.env['op.attendance.line'].sudo().search([('student_id','=',rec.student_id.id),
                                                                             ('attendance_id.course_id.class_id','=',
                                                                              rec.student_id.year_id.id),
                                                                             ('attendance_id.state','=','done')])
            present = len(attendance_lines.filtered(lambda l:l.present))
            all_att = len(attendance_lines)
            if not attendance_lines:
                rec.attendance_percentage = 100
            else:
                rec.attendance_percentage = (present/all_att)
