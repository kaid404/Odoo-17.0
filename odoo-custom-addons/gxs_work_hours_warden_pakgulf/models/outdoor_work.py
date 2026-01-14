# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, timedelta


class TodoTask(models.Model):
    _name = 'outdoor.work'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    request_date = fields.Date('Date')
    phone_id = fields.Char(string='Phone', related="employee_id.work_phone")
    job = fields.Char(string='Job Title', related="employee_id.job_title")
    description = fields.Char(string='Description')
    state = fields.Selection([
        ('draft', "Draft"),
        ('to_approve', "To Approve"),
        ('reject', "Reject"),
        ('approve', "Approved"),
         ], string="Status", default='draft')

    check_in = fields.Datetime(string='Check in')
    check_out = fields.Datetime(string='Check out')
    def create_attendance(self):
        self.env["hr.attendance"].create({
            'employee_id':self.employee_id.id,
            'check_in':self.check_in,
            'check_out':self.check_out
        })
        self.state = 'approve'
    def reject(self):
        self.state = 'reject'
    def to_approve(self):
        self.state = 'to_approve'

    #
    #
    # @api.onchange('request_date', 'employee_id')
    # def _overtime_emp_hour_count(self):
    #     if self.request_date and self.employee_id:
    #         date = fields.Date.to_string(self.request_date - timedelta(days=1))
    #         print(date)
    #         attendance = self.env["hr.attendance"].search(
    #             [('employee_id', '=', self.employee_id.id),
    #              ('checkin_date', '=', date)])
    #         print(attendance)
    #         print(attendance.overtime)
    #         self.request_time = attendance.overtime
    #         self.check_in = attendance.check_in
    #         self.check_out = attendance.check_out
    #         if not self.request_time:
    #             self.attrs_condition = False
    #         elif self.request_time > 2:
    #             self.attrs_condition = True
    #         else:
    #             self.attrs_condition = False
    #
    # def approve(self):
    #     ttendance = self.env["hr.attendance"].search(
    #         [('employee_id', '=', self.employee_id.id),
    #          ('checkin_date', '=', self.request_date)])
    #     ttendance.write({'assumption_request': 'Request Approved'
    #                      })
    #     count_late = self.env["late.check_in"].search(
    #         [('employee_id', '=', self.employee_id.id), ('date', '=', self.request_date)
    #          ])
    #     if count_late:
    #         count_late.unlink()
    #     duplicate = self.env["hr.leave"].search(
    #         [('employee_id', '=', self.employee_id.id), ('date_from', '=', self.request_date),
    #          ('name', '=', 'Late Deduction')
    #          ])
    #
    #     if duplicate:
    #         print(duplicate)
    #         for i in duplicate:
    #             if i.state == 'confirm' or i.state == 'refuse':
    #                 i.action_draft()
    #                 i.unlink()
    #                 break
    #             elif i.state == 'draft':
    #                 i.unlink()
    #             else:
    #                 print('not delet')
    #
    #
