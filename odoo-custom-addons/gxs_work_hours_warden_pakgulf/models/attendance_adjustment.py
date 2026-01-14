from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

import calendar

from pytz import timezone
from odoo.exceptions import UserError, ValidationError
import logging
import pytz

from odoo.tools import float_compare, format_date



from odoo import api, fields, models
from datetime import datetime, time, timedelta, date


class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    planning_count = fields.Integer(compute='_compute_planning_count', string='Planning Count')

    def _compute_planning_count(self):
        planning = self.env['planning.slot'].search([('employee_id', '=', self.id)])
        for employee in self:
            employee.planning_count = len(planning)


class PlannigSlotDate(models.Model):
    _inherit = 'planning.slot'

    new_date = fields.Date('Date-Planned', compute="_get_new_current_plan", store=True, default=False)

    @api.depends('start_datetime')
    def _get_new_current_plan(self):
        for rec in self:
            if rec.start_datetime:
                date = datetime.strftime(rec.start_datetime, '%Y-%m-%d %H:%M:%S')
                new_date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
                rec.new_date = new_date_time



class AttendanceInherit(models.Model):
    _inherit = 'hr.attendance'
    # check_in = fields.Datetime(string="Check In", default=False, required=True)
    # employee_id = fields.Many2one('hr.employee', string="Employee",default=False, required=True, ondelete='cascade', index=True)

    from_date = fields.Date('From Date', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=False)
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=False)
    mint_15 = fields.Datetime(string='15')
    # plan_date_only = fields.Date('Planned Date', compute='_plan_attendance', store=True)

    plan_date_only = fields.Date('Planned Date', compute='_plan_attendance', store=True)
    planned_date = fields.Datetime('Planned Checkin', compute='_plan_attendance', store=True)
    planned_exit = fields.Datetime('Planned Checkout', compute='_plan_attendance', store=True)

    # planned_date = fields.Datetime('Planned Checkin', compute='_plan_attendance', store=True)
    planned_time = fields.Float('Planned Time', compute='_plan_attendance', store=True)
    # planned_exit_time = fields.Float('Planned Checkout', compute='_plan_attendance', store=True)
    checkin_date = fields.Date('Date-Checkin', compute='_get_new_current_checkin', store=True, default=False)
    # checkout_date = fields.Date('Date-Checkout', compute='_get_new_current_checkout', store=True, default=False)
    late_emp = fields.Float('Late', compute="_late_emp_hours", store=True)
    early_emp = fields.Float(string='early_emp',compute="_late_emp_hours", store=True)
    overtime = fields.Float('Overtime', compute='_overtime_emp_hour', store=True)
    assumption_request = fields.Char(string='Assumption Request', readonly=True)

    work_min_time = fields.Boolean(string='Work MIN?',compute="_late_emp_hours",store=True)


    def compute_miss_checkout(self):
        miss_check_outs = self.env["hr.attendance"].search(
            [ ('checkin_date', '=', date.today()),
             ('check_in', '!=', False),('check_out', '=', False)
             ])
        for rec in miss_check_outs:
            first_day = rec.check_in.replace(day=1)

            # Get the last day of the month
            last_day = rec.check_in.replace(day=calendar.monthrange(rec.check_in.year, rec.check_in.month)[1])


            relax_time_id = self.env['gxs.late.policy.dep'].search([
                ('department_ids', 'in', rec.employee_id.department_id.id),
                ('date_from', '<=', rec.checkin_date), ('date_to', '>=', rec.checkin_date)], limit=1,
                order='id desc')

            count_late = self.env["hr.attendance"].search(
                [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                 ('check_in', '!=', False), ('late_emp', '>', 0.0),
                 ('checkin_date', '<=', last_day)
                 ]).ids

            count_early_d = self.env["hr.attendance"].search(
                [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                 ('check_in', '!=', False), ('work_min_time', '!=', False),
                 ('checkin_date', '<=', last_day)
                 ]).ids

            count_early_depar = self.env["hr.attendance"].search(
                [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                 ('check_in', '!=', False), ('early_emp', '>', 0.0),
                 ('checkin_date', '<=', last_day)
                 ]).ids

            miss_checkout = self.env["hr.attendance"].search(
                [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                 ('check_in', '!=', False), ('check_out', '=', False),
                 ('checkin_date', '<=', last_day)
                 ]).ids
            count_late = count_late + count_early_d  + count_early_depar + miss_checkout
            count_late = len(list(set(count_late)))

            count_late_2 = count_late - relax_time_id.per_month
            count_late_deduction = False
            print('kkk',relax_time_id)
            if count_late_2 >1:
                leaves = self.env["hr.leave"].search_count(
                    [('employee_id', '=', rec.employee_id.id),
                     ('date_from', '>=', first_day),
                     ('date_to', '<=', last_day),

                     ('name', '=', 'Late Deduction')
                     ])
                if count_late_2 % relax_time_id.on_each == 0 and leaves == 0:
                    count_late_deduction = True
                if (count_late_2 -  relax_time_id.on_each)% relax_time_id.on_each_for_salary == 0 and leaves == 1:
                    count_late_deduction = True
                print(count_late > relax_time_id.per_month,count_late_2 % 3)
            # if count_late > relax_time_id.per_month and count_late_deduction == True:
            if count_late > relax_time_id.per_month and count_late_deduction == True:

                # print('work', count_late, rec.late_emp, 'nnnnnnnnnnnnnnnnnnnnm', duplicate)
                date_day = rec.check_in.date()
                list_leave_type = ['Exempt Leave','CPL Leave','Sick Leave','Casual Leave','Annual Leave', 'Unpaid']
                if relax_time_id.type == 'by_depart':
                    list_leave_type = relax_time_id.leave_ids
                    # list_leave_type = ['Short leave']
                    for type in list_leave_type:
                        total_leave = 0
                        leave_id = type.leave_id
                        for leave in leave_id:
                            leave_type = leave
                            total_leave = 0
                            employees = rec.employee_id
                            date_from = rec.check_in.date()
                            leave_data = leave_type.get_allocation_data(rec.employee_id, date_from)
                            max_excess = leave_type.max_allowed_negative if leave_type.allows_negative else 0
                            for employee in employees:
                                if leave.name != "Unpaid" and leave.requires_allocation != 'no':
                                    print(leave.name,leave.requires_allocation,max_excess)
                                    print(leave_data)
                                    try:
                                        total_leave = leave_data[employee][0][1]['virtual_remaining_leaves']
                                    except:
                                        total_leave = max_excess
                                # if leave_data[employee][0][1]['total_virtual_excess'] > max_excess:
                            print("total leave========>",total_leave)
                            print("leave data ==========>",leave_data)


                        time_deduction = 1

                        print(leave_id.name,'ddddddd',total_leave
                              ,'sssssss',total_leave)
                        if leave_id.name == 'Unpaid' or 'Short' in leave_id.name:
                            contract = self.env['hr.contract'].search(
                                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')])
                            year = date.today().year
                            month = date.today().month
                            total_days_in_month = calendar.monthrange(year, month)[1]

                            pr_hour = (contract.wage / total_days_in_month)

                            if 'Unpaid' in leave_id.name:
                                late_d = self.env['rst.late.count'].sudo().search(
                                    [('employee_id', '=', rec.employee_id.id),
                                     ('date', '=', rec.checkin_date),
                                     ]).unlink()
                                leaves = self.env["hr.leave"].search_count(
                                    [('employee_id', '=', rec.employee_id.id),
                                     ('date_from', '>=', first_day),
                                     ('date_to', '<=', last_day), ('holiday_status_id', '=', leave_id.id,),
                                     ('name', '=', 'Late Deduction')
                                     ])


                                if leave_id.name == 'Unpaid' and leaves==0:
                                    id = self.env['rst.late.count'].sudo().create({
                                        'name': leave_id.name,
                                        'attendance_id': rec.id,
                                        'employee_id': rec.employee_id.id,
                                        'check_in': rec.check_in,
                                        'check_out': rec.check_out,
                                        'late': rec.late_emp,
                                        'date': rec.checkin_date,
                                        'amount': pr_hour,
                                    })

                                    break



                        else:
                            leaves = self.env["hr.leave"].search_count(
                                [('employee_id', '=', rec.employee_id.id),
                                 ('date_from', '>=', first_day),
                                 ('date_to', '<=', last_day),('holiday_status_id','=', leave_id.id,),('name','=','Late Deduction')
                                 ])
                            if total_leave >= time_deduction and leaves == 0:
                                id = self.env['hr.leave'].create({
                                    'employee_id': rec.employee_id.id,
                                    'date_from': date_day,
                                    'date_to': date_day,
                                    'request_date_from': date_day,
                                    'request_date_to': date_day,
                                    'holiday_status_id': leave_id.id,
                                    'number_of_days': time_deduction,
                                    'name': 'Late Deduction',

                                })
                                print(id)

                                id.action_validate()
                                break




    @api.depends('check_in')
    def _get_new_current_checkin(self):
        karachi_timezone = pytz.timezone('Asia/Karachi')
        for rec in self:
            if rec.check_in:

                date1 = datetime.strftime(rec.check_in, '%Y-%m-%d %H:%M:%S')
                new_checkin = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
                date1 = new_checkin.astimezone(pytz.timezone('Asia/Karachi'))

                rec.checkin_date = date1.date()

            else:
                rec.checkin_date = False

    #
    # @api.depends('check_out')
    # def _get_new_current_checkout(self):
    #     for rec in self:
    #         if rec.check_out:
    #             date = datetime.strftime(rec.check_out, '%Y-%m-%d %H:%M:%S')
    #             new_checkout = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
    #             # print(new_checkin)
    #             rec.checkout_date = new_checkout
    # 
    @api.depends('check_in')
    def _plan_attendance(self):
        for stuff in self:
            plan = self.env['planning.slot'].search(
                [('employee_id', '=', stuff.employee_id.id), ('new_date', '=', stuff.checkin_date)])
            print('pppppp',plan)
            for rec in plan:
                # stuff.plan_date_only = rec.new_date
                stuff.planned_date = rec.start_datetime
                stuff.planned_exit = rec.end_datetime

    @api.constrains('check_in','check_out')
    def _late_emp_hours(self):
        for rec in self:
            if rec.check_in and rec.planned_date:
                late_d = self.env['rst.late.count'].sudo().search(
                    [('employee_id', '=', rec.employee_id.id),
                     ('date', '=', rec.checkin_date),
                     ]).unlink()
                duplicate = self.env["hr.leave"].search(
                    [('employee_id', '=', rec.employee_id.id),
                     ('date_from', '=', rec.checkin_date),
                     ('name', '=', 'Late Deduction')
                     ])
                if duplicate:
                    duplicate.action_refuse()
                    duplicate.action_draft()
                    # duplicate.sudo().unlink()
                    self.env.cr.execute("delete from hr_leave where id=%s" % duplicate.id)
                first_day = rec.check_in.replace(day=1)
                last_day = rec.check_in.replace(day=calendar.monthrange(rec.check_in.year, rec.check_in.month)[1])

                last_month_day = rec.check_in.date().replace(
                    day=calendar.monthrange(rec.check_in.date().year, rec.check_in.date().month)[1])

                date_from_w = rec.check_in.date().replace(day=1).month
                # date_from_w += 1
                date_from_day = rec.check_in.date().day
                if date_from_day <= 20:
                    print('dnvvjnasaxadjn', date_from_day)
                    date_from_w -= 1
                    # date_from = date.strftime(date_from1, f'%Y-{date_from_w}-26')
                    date_from_ytt = rec.check_in.date().replace(day=1)
                    if date_from_w == 0:
                        date_from_y = rec.check_in.date().replace(day=1).year
                        date_from_ytt = rec.check_in.date().replace(day=1)
                        date_from_y -= 1
                        date_from = 1
                        date_from_w = 12
                        date_from = date.strftime(date_from_ytt, f'{date_from_y}-{date_from_w}-21')
                        last_month_day = date.strftime(last_month_day, f'%Y-1-20')
                    else:
                        date_from = date.strftime(date_from_ytt, f'%Y-{date_from_w}-21')
                        date_from_w += 1
                        last_month_day = date.strftime(last_month_day, f'%Y-{date_from_w}-20')


                else:
                    print('iklloj', date_from_day)
                    date_from_w = rec.check_in.date().replace(day=1).month
                    if date_from_w == 12:
                        date_from_y = rec.check_in.date().replace(day=1).year
                        date_from_yww = rec.check_in.date().replace(day=1)
                        date_from_y += 1
                        date_from = 1
                        date_from = date.strftime(date_from_yww, f'%Y-12-21')
                        date_from_w = rec.check_in.date().replace(day=1).month
                        date_from_ww = rec.check_in.date().replace(day=1)
                        last_month_day = date.strftime(date_from_ww, f'{date_from_y}-1-20')
                    else:
                        date_from_ww = rec.check_in.date().replace(day=1)
                        last_month_day = date.strftime(date_from_ww, f'%Y-{date_from_w + 1}-20')
                        date_from_w = rec.check_in.date().replace(day=1).month
                        date_from_ww = rec.check_in.date().replace(day=1)
                        date_from = date.strftime(date_from_ww, f'%Y-{date_from_w}-21')
                        

                first_day = date_from
                last_day = last_month_day
                #raise ValidationError(f"{first_day}/////{last_day}")
                rec.mint_15 = datetime.strftime(rec.check_in, '%Y-%m-%d 00:10:00')
                get_mint_15_up = rec.planned_date - rec.mint_15
                rec.mint_15 = datetime.strftime(rec.check_in, '%Y-%m-%d 00:00:00')
                get_only_time_from_pland = rec.planned_date - rec.mint_15
                get_15_mint = get_only_time_from_pland - get_mint_15_up
                print('check _ in', rec.check_in)
                get_hour = rec.check_in - rec.planned_date
                final_time = get_hour - get_15_mint

                rec.late_emp = get_hour.total_seconds() / 3600
                # print(rec.late_emp,'ppppppppppppppppprr')
                # if rec.late_emp < 0:
                #     rec.late_emp = 0
                # if rec.planned_time == 0:
                #     rec.late_emp = 0
                print('dddddddddddeeeeeeeeeeeeeee')
                if rec.late_emp > 0:

                    # permanent = self.env["hr.contract"].search(
                    #     [('employee_id', '=', rec.employee_id.id),('state' ,'=' ,'open')
                    #      ])
                    relax_time_id = self.env['gxs.late.policy.dep'].search([
                        ('department_ids', 'in', rec.employee_id.department_id.id),
                        ('date_from', '<=', rec.checkin_date), ('date_to', '>=', rec.checkin_date)], limit=1,
                        order='id desc')
                    print('dddddddddddddddddddddddddd')
                    if relax_time_id:
                        relax_time = relax_time_id.time
                        print('1', relax_time)
                        relax_time = (relax_time / 100) * 100
                        print('2', relax_time)
                        # relax_time = relax_time / 100
                        # print('3',relax_time)
                        rec.late_emp = rec.late_emp - relax_time
                        print(rec.late_emp)
                    if rec.late_emp < 0:
                        rec.late_emp = 0

                    # relax_time = self.env['ir.config_parameter'].sudo().get_param("relax_time")
                    #  relax_time = int(relax_time)
                    #  relax_time = (relax_time/60)*100
                    #  relax_time = relax_time/100
                    #  rec.late_emp = rec.late_emp - relax_time
                    if rec.late_emp < 0:
                        rec.late_emp = 0
                    print(rec.late_emp,'ppp')

                if rec.check_out:
                    work_hours = rec.check_out - rec.check_in
                    rec.worked_hours = work_hours.total_seconds() / 3600.0

                if rec.late_emp > 0.0:

                    count_late1 = self.env["hr.attendance"].search(
                        [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                         ('check_in', '!=', False), ('late_emp', '>', 0.0),
                         ('checkin_date', '<=', last_day)
                         ]).ids

                    count_early_d1 = self.env["hr.attendance"].search(
                        [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                         ('checkin_date', '<=', last_day)
                         ])
                    count_early_d = []
                    print(count_early_d1)
                    for dd in count_early_d1:
                        print('dd.work_min_time')
                        print(dd.work_min_time)
                        print(dd.early_emp)
                        if dd.work_min_time == True:
                            count_early_d.append(dd.id)

                    count_early_depar = self.env["hr.attendance"].search(
                        [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                         ('check_in', '!=', False), ('early_emp', '>', 0),
                         ('checkin_date', '<=', last_day)
                         ]).ids

                    miss_checkout = self.env["hr.attendance"].search(
                        [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                         ('check_in', '!=', False), ('check_out', '=', False),
                         ('checkin_date', '<=', last_day)
                         ]).ids
                    count_late = count_late1 + count_early_d + count_early_depar + miss_checkout
                    count_late = len(list(set(count_late)))
                    print('count_early_d,count_early_d,count_early_d')
                    print(count_early_d)
                    print(count_early_d)
                    print(count_early_d)
                    count_late_2 = count_late - relax_time_id.per_month
                    count_late_deduction = False
                    print('kkk',relax_time_id)
                    print('eeeeeeeeeeee333',count_late1, count_late, count_early_d, count_early_depar, miss_checkout,'eeeeeee32',count_late_2,']]',rec.checkin_date)

                    if count_late_2 >0:
                        leaves = self.env["hr.leave"].search_count(
                            [('employee_id', '=', rec.employee_id.id),
                             ('request_date_from', '>=', first_day),
                             ('request_date_from', '<=', last_day),

                             ('name', '=', 'Late Deduction')
                             ])
                        if count_late_2 % relax_time_id.on_each == 0 and leaves == 0:
                            count_late_deduction = True
                        elif (count_late_2 - relax_time_id.on_each) % relax_time_id.on_each_for_salary == 0 and leaves == 1:
                            count_late_deduction = True
                        # else:
                        #     if (count_late_2) % relax_time_id.on_each_for_salary == 0:
                        #         count_late_deduction = True
                        print(rec.checkin_date,'ddddddddddd12')
                        print(count_late1,count_late, count_early_d, count_early_depar, miss_checkout)

                        print(count_late > relax_time_id.per_month, count_late_2 % relax_time_id.on_each,
                              count_late_deduction, leaves)
                        print(count_late > relax_time_id.per_month,
                              (count_late_2 - relax_time_id.on_each) % relax_time_id.on_each_for_salary,
                              count_late_deduction, leaves)                    # if count_late > relax_time_id.per_month and count_late_deduction == True:
                    if count_late > relax_time_id.per_month and count_late_deduction == True:

                        # print('work', count_late, rec.late_emp, 'nnnnnnnnnnnnnnnnnnnnm', duplicate)
                        date_day = rec.check_in.date()
                        list_leave_type = ['Exempt Leave','CPL Leave','Sick Leave','Casual Leave','Annual Leave', 'Unpaid']
                        if relax_time_id.type == 'by_depart':
                            list_leave_type = relax_time_id.leave_ids
                            # list_leave_type = ['Short leave']
                            for type in list_leave_type:
                                total_leave = 0
                                leave_id = type.leave_id
                                print(leave_id.name,rec.check_in.date(),first_day)
                                for leave in leave_id:
                                    leave_type = leave
                                    total_leave = 0
                                    employees = rec.employee_id
                                    date_from = rec.check_in.date()
                                    leave_data = leave_type.get_allocation_data(rec.employee_id, date_from)
                                    max_excess = leave_type.max_allowed_negative if leave_type.allows_negative else 0
                                    for employee in employees:
                                        if leave.name != "Unpaid" and leave.requires_allocation != 'no':
                                            print(leave.name,leave.requires_allocation,max_excess)
                                            print(leave_data)
                                            try:
                                                total_leave = leave_data[employee][0][1]['virtual_remaining_leaves']
                                            except:
                                                total_leave = max_excess
                                        # if leave_data[employee][0][1]['total_virtual_excess'] > max_excess:
                                    print("total leave========>",total_leave)
                                    print("leave data ==========>",leave_data)


                                time_deduction = 1

                                print(leave_id.name,'ddddddd',total_leave
                                      ,'sssssss',total_leave)
                                if leave_id.name == 'Unpaid' or 'Short' in leave_id.name:
                                    contract = self.env['hr.contract'].search(
                                        [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')])
                                    year = date.today().year
                                    month = date.today().month
                                    total_days_in_month = calendar.monthrange(year, month)[1]

                                    pr_hour = (contract.wage / total_days_in_month)
                                    print(count_late_2 - relax_time_id.on_each)
                                    print(count_late_2)
                                    print('---------------------------------------------------------',rec.checkin_date)
                                    print((count_late_2 - relax_time_id.on_each) % relax_time_id.on_each_for_salary)
                                    leaves = self.env["hr.leave"].search_count(
                                        [('employee_id', '=', rec.employee_id.id),
                                         ('date_from', '>=', first_day),
                                         ('date_to', '<=', last_day),

                                         ('name', '=', 'Late Deduction')
                                         ])

                                    leavessss = self.env["hr.leave"].search(
                                        [('employee_id', '=', rec.employee_id.id),
                                         ('request_date_from', '=',rec.checkin_date),

                                         ])

                                    if leavessss:
                                        late_d = self.env['rst.late.count'].sudo().search(
                                            [('employee_id', '=', rec.employee_id.id),
                                             ('date', '=', rec.checkin_date),
                                             ]).unlink()

                                    if  (count_late_2) % relax_time_id.on_each_for_salary == 0 or leaves==1:
                                        print('[[[[[[[[---------------]]]]]]]]]')


                                        if leave_id.name == 'Unpaid' and not leavessss:
                                            late_d = self.env['rst.late.count'].sudo().search(
                                                [('employee_id', '=', rec.employee_id.id),
                                                 ('date', '=', rec.checkin_date),
                                                 ]).unlink()
                                            id = self.env['rst.late.count'].sudo().create({
                                                'name': leave_id.name,
                                                'attendance_id': rec.id,
                                                'employee_id': rec.employee_id.id,
                                                'check_in': rec.check_in,
                                                'check_out': rec.check_out,
                                                'late': rec.late_emp,
                                                'date': rec.checkin_date,
                                                'amount': pr_hour,
                                            })
                                            print('fffffffffffffffffffffff')
                                            print(id)

                                            break



                                else:
                                    leaves = self.env["hr.leave"].search_count(
                                        [('employee_id', '=', rec.employee_id.id),
                                         ('request_date_from', '>=', first_day),
                                         ('request_date_from', '<=', last_day),('holiday_status_id','=', leave_id.id,),('name','=','Late Deduction')
                                         ])
                                    if total_leave >= time_deduction and leaves == 0:
                                        late_d = self.env['rst.late.count'].sudo().search(
                                            [('employee_id', '=', rec.employee_id.id),
                                             ('date', '=', date_day),
                                             ]).unlink()
                                        #raise ValidationError(f'{first_day}////{last_day}////{leave_id}////{date_day}////{rec.employee_id.name}')

                    
                                        id = self.env['hr.leave'].create({
                                            'employee_id': rec.employee_id.id,
                                            'date_from': date_day,
                                            'date_to': date_day,
                                            'request_date_from': date_day,
                                            'request_date_to': date_day,
                                            'holiday_status_id': leave_id.id,
                                            'number_of_days': time_deduction,
                                            'name': 'Late Deduction',

                                        })
                                        print(id)

                                        id.action_validate()
                                        break

                        # if relax_time_id.type == 'global':
                        #     list_leave_type = relax_time_id.late_leave_ids
                        #     # list_leave_type = ['Short leave']
                        #     for type in list_leave_type:
                        #         remaining_leaves = 0
                        #         leave_id = type
                        #         for holiday in leave_id:
                        #             mapped_days = holiday.get_employees_days(
                        #                 (rec.employee_id | rec.employee_id).ids, date_day)
                        #             if rec.employee_id:
                        #                 leave_days = mapped_days[rec.employee_id.id][
                        #                     holiday.id]
                        #                 if float_compare(leave_days['remaining_leaves'], 0,
                        #                                  precision_digits=2) == -1 or float_compare(
                        #                     leave_days['virtual_remaining_leaves'], 0,
                        #                     precision_digits=2) == -1:
                        #                     continue
                        #         remaining_leaves = leave_days['remaining_leaves']
                        #
                        #         total_leave = remaining_leaves
                        #         # if type == 'unpaid':
                        #         #     total_leave = 10
                        #         print("total_leave", total_leave)
                        #
                        #         for lps in type.late_leave_ids:
                        #
                        #             # if rec.late_emp <= lps.deduct_to and rec.late_emp >= lps.deduct_from and total_leave >= lps.deduction:
                        #             #     id = self.env['hr.leave'].create({
                        #             #         'employee_id': rec.employee_id.id,
                        #             #         'date_from': date_day,
                        #             #         'date_to': date_day,
                        #             #         'request_date_from': date_day,
                        #             #         'request_date_to': date_day,
                        #             #         'holiday_status_id': leave_id.id,
                        #             #         'number_of_days': lps.deduction,
                        #             #         'name': 'Late Deduction',
                        #             #
                        #             #     })
                        #
                        #             if count_late == 3:
                        #                 time_deduction = 0.5
                        #             if count_late > 3:
                        #                 time_deduction = 1
                        #
                        #             if total_leave >= time_deduction:
                        #                 id = self.env['hr.leave'].create({
                        #                     'employee_id': rec.employee_id.id,
                        #                     'date_from': date_day,
                        #                     'date_to': date_day,
                        #                     'request_date_from': date_day,
                        #                     'request_date_to': date_day,
                        #                     'holiday_status_id': leave_id.id,
                        #                     'number_of_days': time_deduction,
                        #                     'name': 'Late Deduction',
                        #
                        #                 })
                        #
                        #             id.action_validate()
                        #             break
                        #
                        # leave_id = self.env['hr.leave.type'].search(
                        #     [('is_unpaid', '=', True)])
                        # print('ppppppppp[[[[[[[',leave_id)
                        # for lp in leave_id.late_leave_ids:
                        #
                        #     duplicate = self.env["hr.leave"].search_count(
                        #             [('employee_id', '=', rec.employee_id.id), ('date_from', '=', date_day),
                        #              ('name', '=', 'Late Deduction')
                        #              ])
                        #
                        #     print(rec.late_emp,duplicate)
                        #
                        #     print(lp.deduct_to,'---',)
                        #     if rec.late_emp <= lp.deduct_to and rec.late_emp  >= lp.deduct_from and duplicate == 0:
                        #         late_d = self.env['rst.late.count'].sudo().search(
                        #             [('employee_id', '=', rec.employee_id.id),
                        #              ('date', '=', rec.checkin_date),
                        #              ]).unlink()
                        #         # duplicate = self.env["hr.leave"].search(
                        #         #     [('employee_id', '=', rec.employee_id.id),
                        #         #      ('date_from', '=', rec.checkin_date),
                        #         #      ('name', '=', 'Late Deduction')
                        #         #      ])
                        #         # if duplicate:
                        #         #     duplicate.action_refuse()
                        #         #     duplicate.action_draft()
                        #         #     # duplicate.sudo().unlink()
                        #         #     self.env.cr.execute("delete from hr_leave where id=%s" % duplicate.id)
                        #         id = self.env['hr.leave'].create({
                        #             'employee_id': rec.employee_id.id,
                        #             'date_from': date_day,
                        #             'date_to': date_day,
                        #             'request_date_from': date_day,
                        #             'request_date_to': date_day,
                        #             'holiday_status_id': leave_id.id,
                        #             'number_of_days': lp.deduction,
                        #             'name': 'Late Deduction',
                        #
                        #         })
                        #
                        #         print(id)
                        #         id.action_validate()
                        #         break
                        #     # late_check_in = self.env['late.check_in'].search(
                        #     #     ['&', ('employee_id', '=', rec.employee_id.id), ('description', 'ilike', 'Early Leave'),
                        #     #      ('date', '=', rec.check_in.date())])
                        #     # # print(late_check_in,"late_check_in")
                        #     # count_late = self.env["hr.attendance"].search(
                        #     #     [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', rec.from_date),
                        #     #      ('check_in', '!=', False), ('late_emp', '>', 0),
                        #     #      ('checkin_date', '<=', rec.to_date)
                        #     #      ])
                        #     # duplicate = self.env["hr.leave"].search_count(
                        #     #     [('employee_id', '=', rec.employee_id.id), ('date_from', '=', date_day),
                        #     #      ('name', '=', 'Late Deduction')
                        #     #      ])
                        #     # if rec.late_emp < 4 and rec.late_emp > 2 and not duplicate:
                        #     #     _logger.info('11111111111111111111111111111######################')
                        #     #     _logger.info(rec.employee_id.name)
                        #     #     _logger.info(leave_id.name)
                        #     #     if late_check_in:
                        #     #         late_check_in.unlink()
                        #     #     id = self.env['hr.leave'].create({
                        #     #         'employee_id': rec.employee_id.id,
                        #     #         'date_from': date_day,
                        #     #         'date_to': date_day,
                        #     #         'request_date_from': date_day,
                        #     #         'request_date_to': date_day,
                        #     #         'holiday_status_id': leave_id.id,
                        #     #         'number_of_days': 0.5,
                        #     #         'name': 'Late Deduction',
                        #     #
                        #     #     })
                        #     #
                        #     #     # half_day_salary = per_day_salary / .5
                        #     #     self.env['late.check_in'].create({
                        #     #         'employee_id': rec.employee_id.id,
                        #     #         'late_minutes': rec.late_emp,
                        #     #         'date': rec.check_in.date(),
                        #     #         'attendance_id': rec.id,
                        #     #         'amount': 0.5,
                        #     #         'description': f'Late Deduct from leave {leave_id.name}',
                        #     #     })
                        #     #     print('/..............work')
                        #     #     # id.action_validate()
                        #     #     break
                        #     #
                        #     # elif rec.late_emp > 4 and not duplicate:
                        #     #     _logger.info('222222222222222222222222222222222222222######################')
                        #     #     if late_check_in:
                        #     #         late_check_in.unlink()
                        #     #
                        #     #     id = self.env['hr.leave'].create({
                        #     #         'employee_id': rec.employee_id.id,
                        #     #         'date_from': date_day,
                        #     #         'date_to': date_day,
                        #     #         'request_date_from': date_day,
                        #     #         'request_date_to': date_day,
                        #     #         'holiday_status_id': leave_id.id,
                        #     #         'number_of_days': 1,
                        #     #         'name': 'Late Deduction',
                        #     #
                        #     #     })
                        #     #     # half_day_salary = per_day_salary / .5
                        #     #     self.env['late.check_in'].sudo().create({
                        #     #         'employee_id': rec.employee_id.id,
                        #     #         'late_minutes': rec.late_emp,
                        #     #         'date': rec.check_in.date(),
                        #     #         'attendance_id': rec.id,
                        #     #         'amount': 1,
                        #     #         'description': f'Early Leave Deduct from {leave_id.name}',
                        #     #     })
                        #     #     print('/..............work')
                        #     #     # id.action_validate()
                        #     #     break
                        #     # elif rec.late_emp < 2 and not duplicate:
                        #     #     _logger.info('222222222222222222222222222222222222222######################')
                        #     #     if late_check_in:
                        #     #         late_check_in.unlink()
                        #     #
                        #     #     id = self.env['hr.leave'].create({
                        #     #         'employee_id': rec.employee_id.id,
                        #     #         'date_from': date_day,
                        #     #         'date_to': date_day,
                        #     #         'request_date_from': date_day,
                        #     #         'request_date_to': date_day,
                        #     #         'holiday_status_id': leave_id.id,
                        #     #         'number_of_days': .25,
                        #     #         'name': 'Late Deduction',
                        #     #     })
                        #     #     # half_day_salary = per_day_salary / .5
                        #     #     self.env['late.check_in'].sudo().create({
                        #     #         'employee_id': rec.employee_id.id,
                        #     #         'late_minutes': rec.late_emp,
                        #     #         'date': rec.check_in.date(),
                        #     #         'attendance_id': rec.id,
                        #     #         'amount': 0.25,
                        #     #         'description': f'Early Leave Deduct from {leave_id.name}',
                        #     #     })
                        #     #     print('/..............work')
                        #     #     # id.action_validate()
                        #     #     break


            elif rec.late_emp > 0:
                if rec.late_emp < 0:
                    rec.late_emp = 0

            # check_in_hour = check_in_hour.strftime('%H')
            else:

                rec.late_emp = False


            if rec.check_out:
                # first_day = rec.check_in.replace(day=1)
                #
                # # Get the last day of the month
                # last_day = rec.check_in.replace(day=calendar.monthrange(rec.check_in.year, rec.check_in.month)[1])

                relax_time_id = self.env['gxs.late.policy.dep'].search([
                    ('department_ids', 'in', rec.employee_id.department_id.id),
                    ('date_from', '<=', rec.checkin_date), ('date_to', '>=', rec.checkin_date)], limit=1,
                    order='id desc')
                last_month_day = rec.check_out.date().replace(day=calendar.monthrange(rec.check_out.date().year, rec.check_out.date().month)[1])
                date_from_w = rec.check_out.date().replace(day=1).month
                date_day = rec.check_in.date()
                if rec.check_out:
                    permanent = self.env["hr.contract.history"].search(
                        [('employee_id', '=', rec.employee_id.id)
                         ])
                    if rec.planned_exit:
                        start_dt = fields.Datetime.from_string(rec.check_out)
                        finish_dt = fields.Datetime.from_string(rec.planned_exit)
                        over_hour = start_dt - finish_dt

                        rec.overtime = over_hour.total_seconds() / 3600.0
                        if rec.overtime < 0:
                            if relax_time_id:
                                relax_time = relax_time_id.early_time
                                print('1', relax_time)
                                relax_time = (relax_time / 100) * 100
                                print('2', relax_time)
                                # relax_time = relax_time / 100
                                # print('3',relax_time)
                                print('ffffffffffff',rec.overtime)
                                rec.early_emp = abs(abs(rec.overtime) - relax_time)

                                print(rec.early_emp,'[[[[[[[[[]]]]]]]')
                                print(relax_time_id.half_day_shift,'[[[[[[[[[]]]]]]]',rec.worked_hours)
                                print(relax_time_id.regular_shift,'[[[[[[[[[]]]]]]]',rec.worked_hours)

                        work_hours = rec.check_out - rec.check_in
                        rec.worked_hours = work_hours.total_seconds() / 3600.0
                        day_check = rec.checkin_date.strftime("%A")
                        aaaaa = 0
                        if day_check == 'Saturday':
                            if rec.worked_hours < relax_time_id.half_day_shift:
                                rec.work_min_time = True
                                aaaaa = 1
                            else:
                                rec.work_min_time = False
                        else:
                            if rec.worked_hours < relax_time_id.regular_shift:
                                rec.work_min_time = True
                                aaaaa = 1
                            else:
                                rec.work_min_time = False
                        if rec.overtime < 0:
                            rec.overtime = 0
                        if rec.early_emp > 0.0 or aaaaa == 1:

                            count_late1 = self.env["hr.attendance"].search(
                                [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                                 ('check_in', '!=', False), ('late_emp', '>', 0.0),
                                 ('checkin_date', '<=', last_day)
                                 ]).ids

                            count_early_d = self.env["hr.attendance"].search(
                                [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                                 ('check_in', '!=', False), ('work_min_time', '!=', False),
                                 ('checkin_date', '<=', last_day)
                                 ]).ids

                            count_early_depar = self.env["hr.attendance"].search(
                                [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                                 ('check_in', '!=', False), ('early_emp', '>', 0.0),
                                 ('checkin_date', '<=', last_day)
                                 ]).ids

                            miss_checkout = self.env["hr.attendance"].search(
                                [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
                                 ('check_in', '!=', False), ('check_out', '=', False),
                                 ('checkin_date', '<=', last_day)
                                 ]).ids
                            count_late = count_late1 + count_early_d + count_early_depar + miss_checkout
                            count_late = len(list(set(count_late)))
                            print(count_late,'ffffffffffffff',count_early_d,rec.checkin_date)


                            count_late_2 = count_late - relax_time_id.per_month
                            count_late_deduction = False
                            if count_late_2 > 1:
                                leaves = self.env["hr.leave"].search_count(
                                    [('employee_id', '=', rec.employee_id.id),
                                     ('date_from', '>=', first_day),
                                     ('date_to', '<=', last_day),
                                     ('name', '=', 'Late Deduction')
                                     ])
                                if count_late_2 % relax_time_id.on_each == 0 and leaves==0:
                                    count_late_deduction = True
                                elif (count_late_2 -  relax_time_id.on_each) % relax_time_id.on_each_for_salary == 0 and leaves==1:
                                    count_late_deduction = True
                                print(rec.checkin_date, '4444444444444')
                                print(count_late,count_late1 , count_early_d , count_early_depar , miss_checkout)
                                print(count_late > relax_time_id.per_month, count_late_2 % relax_time_id.on_each,count_late_deduction,leaves)
                                print(count_late > relax_time_id.per_month, (count_late_2 -  relax_time_id.on_each) % relax_time_id.on_each_for_salary,count_late_deduction,leaves)
                            # if count_late > relax_time_id.per_month and count_late_deduction == True:
                            if count_late > relax_time_id.per_month and count_late_deduction == True:

                                # print('work', count_late, rec.late_emp, 'nnnnnnnnnnnnnnnnnnnnm', duplicate)
                                date_day = rec.check_in.date()
                                list_leave_type = ['Exempt Leave', 'CPL Leave', 'Sick Leave', 'Casual Leave',
                                                   'Annual Leave', 'Unpaid']
                                if relax_time_id.type == 'by_depart':
                                    list_leave_type = relax_time_id.leave_ids
                                    # list_leave_type = ['Short leave']
                                    for type in list_leave_type:
                                        total_leave = 0
                                        leave_id = type.leave_id
                                        for leave in leave_id:
                                            leave_type = leave
                                            total_leave = 0
                                            employees = rec.employee_id
                                            date_from = rec.check_in.date()
                                            leave_data = leave_type.get_allocation_data(rec.employee_id, date_from)
                                            max_excess = leave_type.max_allowed_negative if leave_type.allows_negative else 0
                                            for employee in employees:
                                                if leave.name != "Unpaid" and leave.requires_allocation != 'no':
                                                    print(leave.name, leave.requires_allocation, max_excess)
                                                    print(leave_data)
                                                    try:
                                                        total_leave = leave_data[employee][0][1][
                                                            'virtual_remaining_leaves']
                                                    except:
                                                        total_leave = max_excess
                                                # if leave_data[employee][0][1]['total_virtual_excess'] > max_excess:
                                            print("total leave========>", total_leave)
                                            print("leave data ==========>", leave_data)

                                        time_deduction = 1

                                        print(leave_id.name, 'ddddddd', total_leave
                                              , 'sssssss', total_leave)
                                        if leave_id.name == 'Unpaid' or 'Short' in leave_id.name:
                                            contract = self.env['hr.contract'].search(
                                                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')])
                                            year = date.today().year
                                            month = date.today().month
                                            total_days_in_month = calendar.monthrange(year, month)[1]

                                            pr_hour = (contract.wage / total_days_in_month)

                                            if 'Unpaid' in leave_id.name:
                                                print(count_late_2,'---------------------=====',rec.checkin_date)
                                                leaves = self.env["hr.leave"].search_count(
                                                    [('employee_id', '=', rec.employee_id.id),
                                                     ('date_from', '>=', first_day),
                                                     ('date_to', '<=', last_day),

                                                     ('name', '=', 'Late Deduction')
                                                     ])
                                                leavessss = self.env["hr.leave"].search(
                                                    [('employee_id', '=', rec.employee_id.id),
                                                     ('request_date_from', '=', rec.checkin_date),

                                                     ])

                                                if leavessss:
                                                    late_d = self.env['rst.late.count'].sudo().search(
                                                        [('employee_id', '=', rec.employee_id.id),
                                                         ('date', '=', rec.checkin_date),
                                                         ]).unlink()

                                                if  (count_late_2) % relax_time_id.on_each_for_salary == 0 or leaves==1:
                                                    if not leavessss:
                                                        late_d = self.env['rst.late.count'].sudo().search(
                                                            [('employee_id', '=', rec.employee_id.id),
                                                             ('date', '=', rec.checkin_date),
                                                             ]).unlink()
                                                        id = self.env['rst.late.count'].sudo().create({
                                                            'name': leave_id.name,
                                                            'attendance_id': rec.id,
                                                            'employee_id': rec.employee_id.id,
                                                            'check_in': rec.check_in,
                                                            'check_out': rec.check_out,
                                                            'late': rec.late_emp,
                                                            'date': rec.checkin_date,
                                                            'amount': pr_hour,
                                                        })

                                                        break

                                        else:
                                            leaves = self.env["hr.leave"].search_count(
                                                [('employee_id', '=', rec.employee_id.id),
                                                 ('date_from', '>=', first_day),
                                                 ('date_to', '<=', last_day),
                                                 ('holiday_status_id', '=', leave_id.id,),
                                                 ('name', '=', 'Late Deduction')
                                                 ])
                                            if total_leave >= time_deduction and leaves == 0:
                                                late_d = self.env['rst.late.count'].sudo().search(
                                                    [('employee_id', '=', rec.employee_id.id),
                                                     ('date', '=', date_day),
                                                     ]).unlink()
                                                id = self.env['hr.leave'].create({
                                                    'employee_id': rec.employee_id.id,
                                                    'date_from': date_day,
                                                    'date_to': date_day,
                                                    'request_date_from': date_day,
                                                    'request_date_to': date_day,
                                                    'holiday_status_id': leave_id.id,
                                                    'number_of_days': time_deduction,
                                                    'name': 'Late Deduction',

                                                })
                                                print(id)

                                                id.action_validate()
                                                break


                        # leave_id = self.env['hr.leave.type'].search(
                        #     [('name', '=', 'Earned Leave')])
                        # extraHours = self.env['hr.leave.allocation'].create({
                        #     'employee_id': rec.employee_id.id,
                        #     'date_from': date_day,
                        #     'date_to': date_day,
                        #     'holiday_status_id': leave_id.id,
                        #     'number_of_days_display': rec.overtime,
                        #     'name': 'Earned Leave',
                        # })
                        overtime = self.env['gxs.overtime.calculate']
                        if rec.worked_hours:
                            sum_of_time = 0
                            if rec.overtime > 0:
                                sum_of_time += rec.overtime
                            if rec.late_emp < 0:
                                sum_of_time += abs(rec.late_emp)
                            worked_hours = rec.worked_hours - sum_of_time
                            count_early_leave = abs(rec.overtime)
                        state = 0
                        for i in permanent.contract_ids:
                            if i.state == 'open':
                                state = i.per_hour
                        # if rec.overtime > 0 and state != 0:
                        #     lines = overtime.search([
                        #         ('employee_id', '=', rec.employee_id.id),
                        #         ('date_from', '<=', rec.check_in.date()),
                        #         ('date_to', '>=', rec.check_in.date()),
                        #     ])
                        #
                        #     rec.check_in.date()
                        #     over_time = rec.overtime
                        #     state = state
                        #
                        #     if lines:
                        #
                        #         vals = {
                        #             'employee_id': rec.employee_id.id,
                        #             'date': date_day,
                        #             'attendance_id': rec.id,
                        #             'overtime_hours': over_time,
                        #             'total_amount_day': over_time * state,
                        #             'overtime_calculate_id': lines.id,
                        #         }
                        #
                        #         line_id = self.env['gxs.overtime.calculate.lines'].search(
                        #             [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', lines.id)])
                        #         if not line_id and rec.id:
                        #             self.env['gxs.overtime.calculate.lines'].create(vals)
                        #             total = 0
                        #             for las in lines.attendance_ids:
                        #                 total += las.total_amount_day
                        #             lines.total_amount = total
                        #         else:
                        #             line_id.overtime_hours = over_time
                        #             line_id.total_amount_day = over_time * state
                        #             total = 0
                        #             for las in lines.attendance_ids:
                        #                 total += las.total_amount_day
                        #             lines.total_amount = total
                        #     else:
                        #         print(rec.overtime, lines, '2')
                        #         line = overtime.create({
                        #             'employee_id': rec.employee_id.id,
                        #             'date_from': rec.from_date,
                        #             'date_to': rec.to_date,
                        #             'total_amount': over_time * state
                        #         })
                        #
                        #         vals = {
                        #             'employee_id': rec.employee_id.id,
                        #             'attendance_id': rec.id,
                        #             'date': date_day,
                        #             'overtime_hours': over_time,
                        #             'total_amount_day': over_time * state,
                        #             'overtime_calculate_id': line.id,
                        #         }
                        #         line_id = self.env['gxs.overtime.calculate.lines'].search(
                        #             [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', line.id)])
                        #         if not line_id and rec.id:
                        #             self.env['gxs.overtime.calculate.lines'].create(vals)
                        #         else:
                        #             line_id.overtime_hours = over_time
                        #             line_id.total_amount_day = over_time * state

                    else:
                        print('kkkkkkkkkkkkkkkkk')
                        check_out = rec.check_out
                        check_out = check_out.astimezone(pytz.timezone('Asia/Karachi'))
                        # check_in_hour = check_in.strftime('%H')
                        check_out = check_out.strftime('%Y-%m-%d %H:%M:%S')
                        check_out = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
                        # planned_exit_time_str = str(rec.planned_exit_time)
                        # print("::::", planned_exit_time_str)
                        #
                        # h = 0
                        # s = 0
                        # for i in planned_exit_time_str:
                        #     h = h + 1
                        #     if i == '.':
                        #         hour = planned_exit_time_str[0:h - 1]
                        #         if len(hour) == 1:
                        #             hour = '0' + hour
                        #
                        #         mints = planned_exit_time_str[h:]
                        #         if len(mints) == 1:
                        #             mints = '0' + mints
                        #
                        #         rec.mint_15 = datetime.strftime(rec.check_out, f'%Y-%m-%d {hour}:{mints}:%S')

                        start_dt = fields.Datetime.from_string(check_out)
                        finish_dt = fields.Datetime.from_string(rec.mint_15)
                        # over_hour = start_dt - finish_dt
                        work_hours = rec.check_out - rec.check_in
                        rec.worked_hours = work_hours.total_seconds() / 3600.0
                        rec.overtime = rec.worked_hours



                        print(rec.overtime)

                        overtime = self.env['gxs.overtime.calculate']
                        if rec.worked_hours:
                            sum_of_time = 0
                            if rec.overtime > 0:
                                sum_of_time += rec.overtime
                            if rec.late_emp < 0:
                                sum_of_time += abs(rec.late_emp)
                            worked_hours = rec.worked_hours - sum_of_time
                            count_early_leave = abs(rec.overtime)
                        state = 0
                        for i in permanent.contract_ids:
                            if i.state == 'open':

                                if i:
                                    # if rec.overtime < 8:
                                    state = i.per_hour

                        # if rec.overtime > 0 and state != 0:
                        #     lines = overtime.search([
                        #         ('employee_id', '=', rec.employee_id.id),
                        #         ('date_from', '<=', rec.check_in.date()),
                        #         ('date_to', '>=', rec.check_in.date()),
                        #     ])
                        #
                        #     rec.check_in.date()
                        #     over_time = rec.overtime
                        #     state = state
                        #     print(":::::::mmmmmmmmmmmmmmmmmmmmmmm:::::", over_time)
                        #
                        #     if lines:
                        #
                        #         vals = {
                        #             'employee_id': rec.employee_id.id,
                        #             'date': date_day,
                        #             'attendance_id': rec.id,
                        #             'overtime_hours': over_time,
                        #             'total_amount_day': over_time * state,
                        #             'overtime_calculate_id': lines.id,
                        #         }
                        #
                        #         line_id = self.env['gxs.overtime.calculate.lines'].search(
                        #             [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', lines.id)])
                        #         if not line_id and rec.id:
                        #             self.env['gxs.overtime.calculate.lines'].create(vals)
                        #             total = 0
                        #             for las in lines.attendance_ids:
                        #                 total += las.total_amount_day
                        #             lines.total_amount = total
                        #         else:
                        #             line_id.overtime_hours = over_time
                        #             line_id.total_amount_day = over_time * state
                        #             total = 0
                        #             for las in lines.attendance_ids:
                        #                 total += las.total_amount_day
                        #             lines.total_amount = total
                        #     else:
                        #         print(rec.overtime, lines, '2')
                        #         line = overtime.create({
                        #             'employee_id': rec.employee_id.id,
                        #             'date_from': rec.from_date,
                        #             'date_to': rec.to_date,
                        #             'total_amount': over_time * state
                        #         })
                        #
                        #         vals = {
                        #             'employee_id': rec.employee_id.id,
                        #             'attendance_id': rec.id,
                        #             'date': date_day,
                        #             'overtime_hours': over_time,
                        #             'total_amount_day': over_time * state,
                        #             'overtime_calculate_id': line.id,
                        #         }
                        #         line_id = self.env['gxs.overtime.calculate.lines'].search(
                        #             [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', line.id)])
                        #         if not line_id and rec.id:
                        #             self.env['gxs.overtime.calculate.lines'].create(vals)
                        #         else:
                        #             line_id.overtime_hours = over_time
                        #             line_id.total_amount_day = over_time * state
                        #



    @api.constrains('check_out')
    def _overtime_emp_hour(self):


        for rec in self:
            pass
            # if rec.check_out:
            #     first_day = rec.check_in.replace(day=1)
            #
            #     # Get the last day of the month
            #     last_day = rec.check_in.replace(day=calendar.monthrange(rec.check_in.year, rec.check_in.month)[1])
            #     late_d = self.env['rst.late.count'].sudo().search(
            #         [('employee_id', '=', rec.employee_id.id),
            #          ('date', '=', rec.checkin_date),
            #          ]).unlink()
            #     duplicate = self.env["hr.leave"].search(
            #         [('employee_id', '=', rec.employee_id.id),
            #          ('date_from', '=', rec.checkin_date),
            #          ('name', '=', 'Late Deduction')
            #          ])
            #     if duplicate:
            #         duplicate.action_refuse()
            #         duplicate.action_draft()
            #         # duplicate.sudo().unlink()
            #         self.env.cr.execute("delete from hr_leave where id=%s" % duplicate.id)
            #     relax_time_id = self.env['gxs.late.policy.dep'].search([
            #         ('department_ids', 'in', rec.employee_id.department_id.id),
            #         ('date_from', '<=', rec.checkin_date), ('date_to', '>=', rec.checkin_date)], limit=1,
            #         order='id desc')
            #     last_month_day = rec.check_out.date().replace(day=calendar.monthrange(rec.check_out.date().year, rec.check_out.date().month)[1])
            #     date_from_w = rec.check_out.date().replace(day=1).month
            #     date_day = rec.check_in.date()
            #     if rec.check_out:
            #         permanent = self.env["hr.contract.history"].search(
            #             [('employee_id', '=', rec.employee_id.id)
            #              ])
            #         if rec.planned_exit:
            #             start_dt = fields.Datetime.from_string(rec.check_out)
            #             finish_dt = fields.Datetime.from_string(rec.planned_exit)
            #             over_hour = start_dt - finish_dt
            #
            #             rec.overtime = over_hour.total_seconds() / 3600.0
            #             if rec.overtime < 0:
            #                 if relax_time_id:
            #                     relax_time = relax_time_id.early_time
            #                     print('1', relax_time)
            #                     relax_time = (relax_time / 100) * 100
            #                     print('2', relax_time)
            #                     # relax_time = relax_time / 100
            #                     # print('3',relax_time)
            #                     print('ffffffffffff',rec.overtime)
            #                     rec.early_emp = abs(abs(rec.overtime) - relax_time)
            #
            #                     print(rec.early_emp,'[[[[[[[[[]]]]]]]')
            #                     print(relax_time_id.half_day_shift,'[[[[[[[[[]]]]]]]',rec.worked_hours)
            #                     print(relax_time_id.regular_shift,'[[[[[[[[[]]]]]]]',rec.worked_hours)
            #
            #             work_hours = rec.check_out - rec.check_in
            #             rec.worked_hours = work_hours.total_seconds() / 3600.0
            #             day_check = rec.checkin_date.strftime("%A")
            #             if day_check == 'Saturday':
            #                 if rec.worked_hours < relax_time_id.half_day_shift:
            #                     rec.work_min_time = True
            #                 else:
            #                     rec.work_min_time = False
            #             else:
            #                 if rec.worked_hours < relax_time_id.regular_shift:
            #                     rec.work_min_time = True
            #                 else:
            #                     rec.work_min_time = False
            #             if rec.overtime < 0:
            #                 rec.overtime = 0
            #             if rec.early_emp > 0.0:
            #
            #                 count_late1 = self.env["hr.attendance"].search(
            #                     [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
            #                      ('check_in', '!=', False), ('late_emp', '>', 0.0),
            #                      ('checkin_date', '<=', last_day)
            #                      ]).ids
            #
            #                 count_early_d = self.env["hr.attendance"].search(
            #                     [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
            #                      ('check_in', '!=', False), ('work_min_time', '!=', False),
            #                      ('checkin_date', '<=', last_day)
            #                      ]).ids
            #
            #                 count_early_depar = self.env["hr.attendance"].search(
            #                     [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
            #                      ('check_in', '!=', False), ('early_emp', '>', 0.0),
            #                      ('checkin_date', '<=', last_day)
            #                      ]).ids
            #
            #                 miss_checkout = self.env["hr.attendance"].search(
            #                     [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', first_day),('id','<',rec.id+1),
            #                      ('check_in', '!=', False), ('check_out', '=', False),
            #                      ('checkin_date', '<=', last_day)
            #                      ]).ids
            #                 count_late = count_late1 + count_early_d + count_early_depar + miss_checkout
            #                 count_late = len(list(set(count_late)))
            #
            #                 count_late_2 = count_late - relax_time_id.per_month
            #                 count_late_deduction = False
            #                 if count_late_2 > 1:
            #                     leaves = self.env["hr.leave"].search_count(
            #                         [('employee_id', '=', rec.employee_id.id),
            #                          ('date_from', '>=', first_day),
            #                          ('date_to', '<=', last_day),
            #                          ('name', '=', 'Late Deduction')
            #                          ])
            #                     if count_late_2 % relax_time_id.on_each == 0 and leaves==0:
            #                         count_late_deduction = True
            #                     elif (count_late_2 -  relax_time_id.on_each) % relax_time_id.on_each_for_salary == 0 and leaves==1:
            #                         count_late_deduction = True
            #                     print(rec.checkin_date, '4444444444444')
            #                     print(count_late,count_late1 , count_early_d , count_early_depar , miss_checkout)
            #                     print(count_late > relax_time_id.per_month, count_late_2 % relax_time_id.on_each,count_late_deduction,leaves)
            #                     print(count_late > relax_time_id.per_month, (count_late_2 -  relax_time_id.on_each) % relax_time_id.on_each_for_salary,count_late_deduction,leaves)
            #                 # if count_late > relax_time_id.per_month and count_late_deduction == True:
            #                 if count_late > relax_time_id.per_month and count_late_deduction == True:
            #
            #                     # print('work', count_late, rec.late_emp, 'nnnnnnnnnnnnnnnnnnnnm', duplicate)
            #                     date_day = rec.check_in.date()
            #                     list_leave_type = ['Exempt Leave', 'CPL Leave', 'Sick Leave', 'Casual Leave',
            #                                        'Annual Leave', 'Unpaid']
            #                     if relax_time_id.type == 'by_depart':
            #                         list_leave_type = relax_time_id.leave_ids
            #                         # list_leave_type = ['Short leave']
            #                         for type in list_leave_type:
            #                             total_leave = 0
            #                             leave_id = type.leave_id
            #                             for leave in leave_id:
            #                                 leave_type = leave
            #                                 total_leave = 0
            #                                 employees = rec.employee_id
            #                                 date_from = rec.check_in.date()
            #                                 leave_data = leave_type.get_allocation_data(rec.employee_id, date_from)
            #                                 max_excess = leave_type.max_allowed_negative if leave_type.allows_negative else 0
            #                                 for employee in employees:
            #                                     if leave.name != "Unpaid" and leave.requires_allocation != 'no':
            #                                         print(leave.name, leave.requires_allocation, max_excess)
            #                                         print(leave_data)
            #                                         try:
            #                                             total_leave = leave_data[employee][0][1][
            #                                                 'virtual_remaining_leaves']
            #                                         except:
            #                                             total_leave = max_excess
            #                                     # if leave_data[employee][0][1]['total_virtual_excess'] > max_excess:
            #                                 print("total leave========>", total_leave)
            #                                 print("leave data ==========>", leave_data)
            #
            #                             time_deduction = 1
            #
            #                             print(leave_id.name, 'ddddddd', total_leave
            #                                   , 'sssssss', total_leave)
            #                             if leave_id.name == 'Unpaid' or 'Short' in leave_id.name:
            #                                 contract = self.env['hr.contract'].search(
            #                                     [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')])
            #                                 year = date.today().year
            #                                 month = date.today().month
            #                                 total_days_in_month = calendar.monthrange(year, month)[1]
            #
            #                                 pr_hour = (contract.wage / total_days_in_month)
            #
            #                                 if 'Unpaid' in leave_id.name:
            #
            #                                     if leave_id.name == 'Unpaid':
            #                                         id = self.env['rst.late.count'].sudo().create({
            #                                             'name': leave_id.name,
            #                                             'attendance_id': rec.id,
            #                                             'employee_id': rec.employee_id.id,
            #                                             'check_in': rec.check_in,
            #                                             'check_out': rec.check_out,
            #                                             'late': rec.late_emp,
            #                                             'date': rec.checkin_date,
            #                                             'amount': pr_hour,
            #                                         })
            #
            #                                         break
            #
            #                             else:
            #                                 leaves = self.env["hr.leave"].search_count(
            #                                     [('employee_id', '=', rec.employee_id.id),
            #                                      ('date_from', '>=', first_day),
            #                                      ('date_to', '<=', last_day),
            #                                      ('holiday_status_id', '=', leave_id.id,),
            #                                      ('name', '=', 'Late Deduction')
            #                                      ])
            #                                 if total_leave >= time_deduction and leaves == 0:
            #                                     id = self.env['hr.leave'].create({
            #                                         'employee_id': rec.employee_id.id,
            #                                         'date_from': date_day,
            #                                         'date_to': date_day,
            #                                         'request_date_from': date_day,
            #                                         'request_date_to': date_day,
            #                                         'holiday_status_id': leave_id.id,
            #                                         'number_of_days': time_deduction,
            #                                         'name': 'Late Deduction',
            #
            #                                     })
            #                                     print(id)
            #
            #                                     id.action_validate()
            #                                     break
            #
            #
            #             # leave_id = self.env['hr.leave.type'].search(
            #             #     [('name', '=', 'Earned Leave')])
            #             # extraHours = self.env['hr.leave.allocation'].create({
            #             #     'employee_id': rec.employee_id.id,
            #             #     'date_from': date_day,
            #             #     'date_to': date_day,
            #             #     'holiday_status_id': leave_id.id,
            #             #     'number_of_days_display': rec.overtime,
            #             #     'name': 'Earned Leave',
            #             # })
            #             overtime = self.env['gxs.overtime.calculate']
            #             if rec.worked_hours:
            #                 sum_of_time = 0
            #                 if rec.overtime > 0:
            #                     sum_of_time += rec.overtime
            #                 if rec.late_emp < 0:
            #                     sum_of_time += abs(rec.late_emp)
            #                 worked_hours = rec.worked_hours - sum_of_time
            #                 count_early_leave = abs(rec.overtime)
            #             state = 0
            #             for i in permanent.contract_ids:
            #                 if i.state == 'open':
            #                     state = i.per_hour
            #             if rec.overtime > 0 and state != 0:
            #                 lines = overtime.search([
            #                     ('employee_id', '=', rec.employee_id.id),
            #                     ('date_from', '<=', rec.check_in.date()),
            #                     ('date_to', '>=', rec.check_in.date()),
            #                 ])
            #
            #                 rec.check_in.date()
            #                 over_time = rec.overtime
            #                 state = state
            #
            #                 if lines:
            #
            #                     vals = {
            #                         'employee_id': rec.employee_id.id,
            #                         'date': date_day,
            #                         'attendance_id': rec.id,
            #                         'overtime_hours': over_time,
            #                         'total_amount_day': over_time * state,
            #                         'overtime_calculate_id': lines.id,
            #                     }
            #
            #                     line_id = self.env['gxs.overtime.calculate.lines'].search(
            #                         [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', lines.id)])
            #                     if not line_id and rec.id:
            #                         self.env['gxs.overtime.calculate.lines'].create(vals)
            #                         total = 0
            #                         for las in lines.attendance_ids:
            #                             total += las.total_amount_day
            #                         lines.total_amount = total
            #                     else:
            #                         line_id.overtime_hours = over_time
            #                         line_id.total_amount_day = over_time * state
            #                         total = 0
            #                         for las in lines.attendance_ids:
            #                             total += las.total_amount_day
            #                         lines.total_amount = total
            #                 else:
            #                     print(rec.overtime, lines, '2')
            #                     line = overtime.create({
            #                         'employee_id': rec.employee_id.id,
            #                         'date_from': rec.from_date,
            #                         'date_to': rec.to_date,
            #                         'total_amount': over_time * state
            #                     })
            #
            #                     vals = {
            #                         'employee_id': rec.employee_id.id,
            #                         'attendance_id': rec.id,
            #                         'date': date_day,
            #                         'overtime_hours': over_time,
            #                         'total_amount_day': over_time * state,
            #                         'overtime_calculate_id': line.id,
            #                     }
            #                     line_id = self.env['gxs.overtime.calculate.lines'].search(
            #                         [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', line.id)])
            #                     if not line_id and rec.id:
            #                         self.env['gxs.overtime.calculate.lines'].create(vals)
            #                     else:
            #                         line_id.overtime_hours = over_time
            #                         line_id.total_amount_day = over_time * state
            #
            #         else:
            #             print('kkkkkkkkkkkkkkkkk')
            #             check_out = rec.check_out
            #             check_out = check_out.astimezone(pytz.timezone('Asia/Karachi'))
            #             # check_in_hour = check_in.strftime('%H')
            #             check_out = check_out.strftime('%Y-%m-%d %H:%M:%S')
            #             check_out = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
            #             # planned_exit_time_str = str(rec.planned_exit_time)
            #             # print("::::", planned_exit_time_str)
            #             #
            #             # h = 0
            #             # s = 0
            #             # for i in planned_exit_time_str:
            #             #     h = h + 1
            #             #     if i == '.':
            #             #         hour = planned_exit_time_str[0:h - 1]
            #             #         if len(hour) == 1:
            #             #             hour = '0' + hour
            #             #
            #             #         mints = planned_exit_time_str[h:]
            #             #         if len(mints) == 1:
            #             #             mints = '0' + mints
            #             #
            #             #         rec.mint_15 = datetime.strftime(rec.check_out, f'%Y-%m-%d {hour}:{mints}:%S')
            #
            #             start_dt = fields.Datetime.from_string(check_out)
            #             finish_dt = fields.Datetime.from_string(rec.mint_15)
            #             # over_hour = start_dt - finish_dt
            #             work_hours = rec.check_out - rec.check_in
            #             rec.worked_hours = work_hours.total_seconds() / 3600.0
            #             rec.overtime = rec.worked_hours
            #
            #
            #
            #             print(rec.overtime)
            #
            #             overtime = self.env['gxs.overtime.calculate']
            #             if rec.worked_hours:
            #                 sum_of_time = 0
            #                 if rec.overtime > 0:
            #                     sum_of_time += rec.overtime
            #                 if rec.late_emp < 0:
            #                     sum_of_time += abs(rec.late_emp)
            #                 worked_hours = rec.worked_hours - sum_of_time
            #                 count_early_leave = abs(rec.overtime)
            #             state = 0
            #             for i in permanent.contract_ids:
            #                 if i.state == 'open':
            #
            #                     if i:
            #                         # if rec.overtime < 8:
            #                         state = i.per_hour
            #
            #             if rec.overtime > 0 and state != 0:
            #                 lines = overtime.search([
            #                     ('employee_id', '=', rec.employee_id.id),
            #                     ('date_from', '<=', rec.check_in.date()),
            #                     ('date_to', '>=', rec.check_in.date()),
            #                 ])
            #
            #                 rec.check_in.date()
            #                 over_time = rec.overtime
            #                 state = state
            #                 print(":::::::mmmmmmmmmmmmmmmmmmmmmmm:::::", over_time)
            #
            #                 if lines:
            #
            #                     vals = {
            #                         'employee_id': rec.employee_id.id,
            #                         'date': date_day,
            #                         'attendance_id': rec.id,
            #                         'overtime_hours': over_time,
            #                         'total_amount_day': over_time * state,
            #                         'overtime_calculate_id': lines.id,
            #                     }
            #
            #                     line_id = self.env['gxs.overtime.calculate.lines'].search(
            #                         [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', lines.id)])
            #                     if not line_id and rec.id:
            #                         self.env['gxs.overtime.calculate.lines'].create(vals)
            #                         total = 0
            #                         for las in lines.attendance_ids:
            #                             total += las.total_amount_day
            #                         lines.total_amount = total
            #                     else:
            #                         line_id.overtime_hours = over_time
            #                         line_id.total_amount_day = over_time * state
            #                         total = 0
            #                         for las in lines.attendance_ids:
            #                             total += las.total_amount_day
            #                         lines.total_amount = total
            #                 else:
            #                     print(rec.overtime, lines, '2')
            #                     line = overtime.create({
            #                         'employee_id': rec.employee_id.id,
            #                         'date_from': rec.from_date,
            #                         'date_to': rec.to_date,
            #                         'total_amount': over_time * state
            #                     })
            #
            #                     vals = {
            #                         'employee_id': rec.employee_id.id,
            #                         'attendance_id': rec.id,
            #                         'date': date_day,
            #                         'overtime_hours': over_time,
            #                         'total_amount_day': over_time * state,
            #                         'overtime_calculate_id': line.id,
            #                     }
            #                     line_id = self.env['gxs.overtime.calculate.lines'].search(
            #                         [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', line.id)])
            #                     if not line_id and rec.id:
            #                         self.env['gxs.overtime.calculate.lines'].create(vals)
            #                     else:
            #                         line_id.overtime_hours = over_time
            #                         line_id.total_amount_day = over_time * state
