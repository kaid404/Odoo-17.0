from odoo import models, fields, api


class HRContractInerit(models.Model):
    _inherit = "hr.contract"

    per_hour = fields.Float(string="Per Hour")


class HROvertimeCalculate(models.Model):
    _name = "gxs.overtime.calculate"
    # _name = "hr.overtime.calculate.abc"
    _description = "Hr Overtime Calculate"
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string="Employee")
    total_amount = fields.Float(string="Total")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    attendance_ids = fields.One2many('gxs.overtime.calculate.lines', 'overtime_calculate_id', string="Attendances")
    # .attendance_ids = fields.One2many('hr.overtime.calculate.lines', 'overtime_calculate_id', string="Attendances")


class HROvertimeCalculateLines(models.Model):
    _name = "gxs.overtime.calculate.lines"

    attendance_id = fields.Many2one('hr.attendance', string="Employee")
    employee_id = fields.Many2one('hr.employee', string="Employee", related='attendance_id.employee_id')
    overtime_calculate_id = fields.Many2one('gxs.overtime.calculate')
    total_amount_day = fields.Float(string="Total")
    overtime_hours = fields.Float(string="Overtime Hours")
    date = fields.Date(string="Date")
    date_check_in = fields.Datetime(string="Date Check In", related='attendance_id.check_in')
    date_check_out = fields.Datetime(string="Date Check Out", related='attendance_id.check_out')
