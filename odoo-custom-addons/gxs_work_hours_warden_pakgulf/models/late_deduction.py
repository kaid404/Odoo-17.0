from odoo import _, api, fields, models
import calendar
import logging
from datetime import datetime ,date

_logger = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'
    is_overtime = fields.Boolean('Over Time')
    is_late_decution = fields.Boolean('Late Deduction')
    earn_leave = fields.Boolean('Earn Leave')
    sick_leave = fields.Boolean('Sick Leave')


class RstmotoReworkInput(models.Model):
    _name = 'rst.late.count'

    name = fields.Char('name')
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee",realted='attendance_id.employee_id')
    attendance_id = fields.Many2one(comodel_name='hr.attendance', string="Attendance")
    check_in = fields.Datetime(string="Check In",realted='attendance_id.check_in')
    check_out = fields.Datetime(string="Check Out",realted='attendance_id.check_out')
    amount = fields.Float(string="Amount")
    late = fields.Float(string="Late",realted='attendance_id.late_emp')
    date = fields.Date(string='Date',realted='attendance_id.checkin_date')













