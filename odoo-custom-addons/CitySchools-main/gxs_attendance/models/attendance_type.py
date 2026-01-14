from odoo import models, fields


class OpAttendanceType(models.Model):
    _name = "op.attendance.type"
    _inherit = ["mail.thread"]
    _description = "Attendance Type"

    name = fields.Char(
        'Name', size=20, required=True, tracking=True)
    active = fields.Boolean(default=True)
    present = fields.Boolean(
        'Present ?', tracking=True)
    excused = fields.Boolean(
        'Excused ?', tracking=True)
    absent = fields.Boolean('Absent', tracking=True)
    late = fields.Boolean('Late', tracking=True)
