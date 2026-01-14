# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, time, timedelta,date
import pytz

class TodoTask(models.Model):
    _name = 'remote.work'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    phone_id = fields.Char( string='Phone',related="employee_id.work_phone")
    job = fields.Char( string='Job Title', related="employee_id.job_title")
    request_date = fields.Date('Date')
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
        for stuff in self:

            day_check = self.request_date.strftime("%A")
            if day_check == 'Monday':
                check = 0
            if day_check == 'Tuesday':
                check = 1
            if day_check == 'Wednesday':
                check = 2
            if day_check == 'Thursday':
                check = 3
            if day_check == 'Friday':
                check = 4
            if day_check == 'Saturday':
                check = 5
            if day_check == 'Sunday':
                check=6
            plan = self.env['hr.contract.history'].search(
                [('employee_id', '=', stuff.employee_id.id)])
            plan = plan.resource_calendar_id
            plan_day_name = self.env['resource.calendar.attendance'].search(
                [('calendar_id','=',plan.id),('dayofweek', '=', check)])
            planned_time_str = str(plan_day_name.hour_from)
            planned_time_list = list(planned_time_str)
            h = 0

            for i in planned_time_str:
                h = h + 1
                if i == '.':
                    hour = planned_time_str[0:h - 1]
                    if len(hour) >= 1:
                        hour = int(hour) - 5
                    if hour < 0:
                        hour = -(hour)
                    hour = str(hour)
                    if len(hour) == 1:
                        hour = '0' + hour



                    mints = planned_time_str[h:]
                    if len(mints) == 1:
                        mints = '0' + mints
                    self.check_in = datetime.strftime(self.request_date, '%Y-%m-%d 00:15:00')
                    self.check_in = datetime.strftime(self.check_in, f'%Y-%m-%d {hour}:{mints}:%S')
                    check_in = self.check_in
                    check_in = check_in.astimezone(pytz.timezone('Asia/Karachi'))
                    # check_in_hour = check_in.strftime('%H')
                    check_in = check_in.strftime('%Y-%m-%d %H:%M:%S')
                    check_in = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')

            planned_time_str = str(plan_day_name.hour_to)
            planned_time_list = list(planned_time_str)
            h = 0

            for i in planned_time_str:
                h = h + 1
                if i == '.':
                    hour = planned_time_str[0:h - 1]
                    if len(hour) >= 1:
                        hour = int(hour) - 5
                    if hour < 0:
                        hour = -(hour)
                    hour = str(hour)
                    print(type(hour))
                    if len(hour) == 1:
                        hour = '0' + hour

                    mints = planned_time_str[h:]
                    if len(mints) == 1:
                        mints = '0' + mints
                    self.check_out = datetime.strftime(self.request_date, '%Y-%m-%d 00:15:00')
                    self.check_out = datetime.strftime(self.check_out, f'%Y-%m-%d {hour}:{mints}:%S')
                    check_out = self.check_out
                    check_out = check_out.astimezone(pytz.timezone('Asia/Karachi'))
                    # check_in_hour = check_in.strftime('%H')
                    check_out = check_out.strftime('%Y-%m-%d %H:%M:%S')
                    check_out = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')

            # for rec in plan_day_name:
            #     # stuff.plan_date_only = rec.new_date
            #     stuff.planned_time = rec.hour_from
            #     stuff.planned_exit_time = rec.hour_to
        print(self.check_in)
        print(self.check_out)

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
