from odoo import fields, models,api
from datetime import datetime ,date
import calendar




class EmployeeGatePass(models.Model):
    _name = 'employee.attendance.absent'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee GatePass"

    badge_id = fields.Char(string='ID #', related='name.barcode')
    amount_deduc = fields.Float(string='Amount Deduct')
    date = fields.Date(string='Date')
    time_out = fields.Datetime(string='Time Out')
    time_in = fields.Datetime(string='Time In')
    total_time = fields.Float(string='Total Time', compute='_compute_total_time', store=True)
    name = fields.Many2one('hr.employee', string='Name')
    department = fields.Many2one('hr.department',related='name.department_id', string='Department')

    def make_absent(self):


        year = date.today().year
        month = date.today().month
        total_days_in_month = calendar.monthrange(year, month)[1]



        plan = self.env['planning.slot'].search([('new_date', '=', date.today())]).mapped('employee_id.id')
        attendance = self.env['hr.attendance'].search([('checkin_date', '=', date.today())]).mapped('employee_id.id')

        absent  = list(set(plan) - set(attendance))

        unpaid = self.env["hr.leave"].search(
            [('employee_id', 'in', absent), ('request_date_from', '>=', date.today()),
             ('request_date_to', '<=', date.today()), ('holiday_status_id.name', '!=', 'Unpaid')]).mapped('employee_id.id')

        absent = list(set(absent) - set(unpaid))



        # plan = self.env['planning.slot'].search(
        #     [('employee_id', 'in', absent), ('new_date', '=', date.today())])
        # allocated_hours = {}
        # for pl in plan:
        #     allocated_hours.update({pl.employee_id.id:pl.allocated_hours})



        wage = {}
        contract = self.env['hr.contract'].search([('employee_id','in',absent),('state','=','open')])
        for cn in contract:
            # allocated_hours_per_employee = allocated_hours.get(cn.employee_id.id)
            # per_hours = cn.wage/total_days_in_month
            # per_hours = per_hours/allocated_hours_per_employee
            wage.update({cn.employee_id.id:cn.wage/total_days_in_month})


        for rec in absent:
            self.env['employee.attendance.absent'].create({'name':rec,'date':date.today(),'amount_deduc':wage.get(rec)})


