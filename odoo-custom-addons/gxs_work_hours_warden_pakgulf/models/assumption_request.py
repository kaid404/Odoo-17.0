# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date,timedelta
from odoo.exceptions import UserError, ValidationError, MissingError
# access_assumption_request,access.assumption.request,model_assumption_request,,1,1,1,1
# access_outdoor_work,access.outdoor.work,model_outdoor_work,,1,1,1,1
# access_remote_work,access.remote.work,model_remote_work,,1,1,1,1
# access_shift_change_request,access.shift.change.request,model_shift_change_request,,1,1,1,1
class TodoTask(models.Model):
    _name = 'assumption.request'
     
    employee_id = fields.Many2one('hr.employee',string='Employee')
    request_date = fields.Date('Date')
    description = fields.Char(string='Description')
    request_time = fields.Float(string='Overtime' ,compute='_overtime_emp_hour_count', store=True,readonly=True)
    check_in = fields.Datetime(string='Check in',readonly=True, store=True)
    check_out = fields.Datetime(string='Check out',readonly=True, store=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('to_approve', "To Approve"),
        ('reject', "Reject"),
        ('approve', "Approved"),
    ], string="Status", default='draft')

    attrs_condition = fields.Boolean(string='con')
    
    @api.onchange('request_date','employee_id')
    def _overtime_emp_hour_count(self):
        if self.request_date and self.employee_id:
            date = fields.Date.to_string(self.request_date - timedelta(days=1))
            print(date)
            attendance = self.env["hr.attendance"].search(
                [('employee_id', '=', self.employee_id.id),
                   ('checkin_date', '=', date)])
            print(attendance)
            print(attendance.overtime)
            self.request_time = attendance.overtime
            self.check_in = attendance.check_in
            self.check_out = attendance.check_out
            # if not self.request_time:
            #     self.attrs_condition = False
            # elif self.request_time >2:
            #     self.attrs_condition = True
            # else:
            #     self.attrs_condition = False
    def reject(self):
        self.state = 'reject'
    def to_approve(self):
        self.state = 'to_approve'

    def approve(self):
        if self.request_time <= 2:
            raise ValidationError(f"{self.employee_id.name} cannot apply request")
        ttendance = self.env["hr.attendance"].search(
            [('employee_id', '=', self.employee_id.id),
             ('checkin_date', '=', self.request_date)])
        ttendance.write({'assumption_request': 'Request Approved'
                          })
        count_late = self.env["late.check_in"].search(
            [('employee_id', '=', self.employee_id.id), ('date', '=', self.request_date)
             ])
        if count_late:

            count_late.unlink()
        duplicate = self.env["hr.leave"].search(
            [('employee_id', '=', self.employee_id.id), ('date_from', '=', self.request_date),
             ('name','=','Late Deduction')
             ])

        if duplicate:
            print(duplicate,'ll')
            for i in duplicate:
                i.action_refuse()
                i.action_draft()
                i.unlink()


        self.state = 'approve'