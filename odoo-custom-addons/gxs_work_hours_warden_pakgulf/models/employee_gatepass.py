from odoo import fields, models,api
from datetime import datetime ,date
import calendar

from odoo.tools import float_compare, format_date


class HrContract(models.Model):
    _inherit = 'hr.contract'

    per_hour = fields.Float(string="Per Hour",compute="get_overtime_amount")

    @api.depends('wage','resource_calendar_id')
    def get_overtime_amount(self):
        for contract in self:
            # rec = self.env['hr.attendance'].search([('employee_id', '=', contract.employee_id.id)], limit=1, order='id desc')
            #
            year = date.today().year
            month = date.today().month
            #
            # # Calculate the total number of days in the month
            total_days_in_month = calendar.monthrange(year, month)[1]
            # if rec:
            #     planned_time_str = str(rec.planned_time)
            #     planned_time_list = list(planned_time_str)
            #     h = 0
            #
            #     for i in planned_time_str:
            #         h = h + 1
            #         if i == '.':
            #             hour = planned_time_str[0:h - 1]
            #             if len(hour) == 1:
            #                 hour = '0' + hour
            #
            #             mints = planned_time_str[h:]
            #             if len(mints) == 1:
            #                 mints = '0' + mints
            #
            #             rec.mint_15 = datetime.strftime(rec.check_in, f'%Y-%m-%d {hour}:{mints}:%S')
            #
            #     planned_exit_time_str = str(rec.planned_exit_time)
            #
            #     h = 0
            #     s = 0
            #     for i in planned_exit_time_str:
            #         h = h + 1
            #         if i == '.':
            #             hour = planned_exit_time_str[0:h - 1]
            #             if len(hour) == 1:
            #                 hour = '0' + hour
            #
            #             mints = planned_exit_time_str[h:]
            #             if len(mints) == 1:
            #                 mints = '0' + mints
            #
            #             rec.mint_out = datetime.strftime(rec.check_in, f'%Y-%m-%d {hour}:{mints}:%S')
            #
            #     work_hours = rec.mint_out - rec.mint_15
            #     shift_time = work_hours.total_seconds() / 3600.0
            shift_time = contract.resource_calendar_id.hours_per_day

            # if rec:
            contract.per_hour = ((contract.wage / total_days_in_month) / shift_time)*1.5
            print(contract.wage,total_days_in_month,shift_time,'eeeeeeeeeee')

            # else:
            #     contract.per_hour = ((contract.wage / total_days_in_month) / 8)*1.5
            #
            #     print(contract.wage,total_days_in_month)


class EmployeeGatePass(models.Model):
    _name = 'employee.gatepass'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee GatePass"

    name_leave = fields.Char(string='Name')
    badge_id = fields.Char(string='ID #', related='name.barcode')
    amount_deduc = fields.Float(string='Amount Deduct')
    date = fields.Date(string='Date')
    time_out = fields.Datetime(string='Time Out')
    time_in = fields.Datetime(string='Time In')
    total_time = fields.Float(string='Total Time', compute='_compute_total_time', store=True)
    name = fields.Many2one('hr.employee', string='Name')
    department = fields.Many2one('hr.department',related='name.department_id', string='Department')
    gate_pass_type = fields.Selection([
        ('personal', 'Personal'),
        ('official', 'Official'),
    ], string='Type')
    description = fields.Text(string='Purpose')
    image = fields.Binary(string='Image', readonly=False)
    


    def action_time_out(self):
        self.time_out = datetime.now()
        self.date = datetime.now().date()
    
    def action_time_in(self):
        # self.time_in = datetime.now()
        # self.date = datetime.now().date()

        first_day = self.date.replace(day=1)

        # Get the last day of the month
        last_day = self.date.replace(day=calendar.monthrange(self.date.year, self.date.month)[1])

        contract = self.env['hr.contract'].search([('employee_id','=',self.name.id),('state','=','open')])
        # rec = self.env['hr.attendance'].search([('employee_id','=',self.name.id)],limit=1, order='id desc')

        year = date.today().year
        month = date.today().month

        # Calculate the total number of days in the month
        total_days_in_month = calendar.monthrange(year, month)[1]


        plan = self.env['planning.slot'].search(
            [('employee_id', '=', self.name.id), ('new_date', '=', self.date)])
        pr_hour = (contract.wage/total_days_in_month) / plan.allocated_hours

        if self.gate_pass_type == 'official':
            pr_hour = 0

        date_day = date.today()
        day_check = date_day.strftime("%A")

        if day_check == 'Friday':
            in_time = datetime.strftime(datetime.now(), f'%Y-%m-%d {13}:{00}:%S')
            in_time = datetime.strptime(in_time, f'%Y-%m-%d {13}:{00}:%S')
            out_time = datetime.strftime(datetime.now(), f'%Y-%m-%d {14}:{30}:%S')
            out_time = datetime.strptime(out_time, f'%Y-%m-%d {14}:{30}:%S')
        else:
            in_time = datetime.strftime(datetime.now(), f'%Y-%m-%d {13}:{00}:%S')
            in_time = datetime.strptime(in_time, f'%Y-%m-%d {13}:{00}:%S')
            out_time = datetime.strftime(datetime.now(), f'%Y-%m-%d {14}:{00}:%S')
            out_time = datetime.strptime(out_time, f'%Y-%m-%d {14}:{00}:%S')

        relax_time_id = self.env['gxs.late.policy.dep'].search([
            ('department_ids', 'in', self.name.department_id.id),
            ('date_from', '<=', self.date), ('date_to', '>=', self.date)], limit=1,
            order='id desc')

        list_leave_type = relax_time_id.leave_ids
        # list_leave_type = ['Short leave']
        for type in list_leave_type:
            remaining_leaves = 0
            leave_id = type.leave_id
            for holiday in leave_id:
                mapped_days = holiday.get_employees_days(
                    (self.name | self.name).ids, date_day)
                if self.name:
                    leave_days = mapped_days[self.name.id][
                        holiday.id]
                    if float_compare(leave_days['remaining_leaves'], 0,
                                     precision_digits=2) == -1 or float_compare(
                        leave_days['virtual_remaining_leaves'], 0,
                        precision_digits=2) == -1:
                        continue
            remaining_leaves = leave_days['remaining_leaves']

            total_leave = remaining_leaves
            # if type == 'unpaid':
            #     total_leave = 10
            print("total_leave", total_leave)

            # if rec.late_emp <= type.deduct_to and rec.late_emp  >= type.deduct_from and total_leave >= type.deduction:
            #     id = self.env['hr.leave'].create({
            #         'employee_id': rec.employee_id.id,
            #         'date_from': date_day,
            #         'date_to': date_day,
            #         'request_date_from': date_day,
            #         'request_date_to': date_day,
            #         'holiday_status_id': leave_id.id,
            #         'number_of_days': type.deduction,
            #         'name': 'Late Deduction',
            #
            #     })

            # if rec.late_emp <= type.deduct_to and rec.late_emp >= type.deduct_from and total_leave >= type.deduction:

            time_deduction = 0.5

            print(leave_id.name, 'ddddddd', total_leave
                  , 'sssssss', total_leave)
            if leave_id.name == 'Unpaid' or 'Short' in leave_id.name:
                # contract = self.env['hr.contract'].search(
                #     [('employee_id', '=', self.name.id), ('state', '=', 'open')])
                # year = date.today().year
                # month = date.today().month
                # total_days_in_month = calendar.monthrange(year, month)[1]

                # pr_hour = (contract.wage / total_days_in_month) / 2

                if 'Short' in leave_id.name:
                    id = self.env['rst.late.count'].sudo().search_count([('name', '=', leave_id.name),
                                                                         ('date', '>=', first_day),
                                                                         ('date', '<=', last_day),
                                                                         ('employee_id', '=', self.name.id)])
                    self.name_leave = ''

                    gate = self.env['employee.gatepass'].sudo().search_count([('name_leave', '=', leave_id.name),
                                                                         ('date', '>=', first_day),
                                                                         ('date', '<=', last_day),
                                                                              ('name', '=', self.name.id)])

                    leave_count = self.env['hr.leave'].sudo().search_count(
                        [('holiday_status_id', '=', leave_id.id),
                         ('date_from', '<=', first_day), ('date_from', '>=', last_day),('employee_id', '=', self.name.id)])

                    print('ffffffffff',last_day,first_day)
                    print('ffffffffff',leave_count,id,gate,self.date,self.name.name)
                    if (int(id + leave_count + gate)) > 1:
                        pass
                    else:
                        self.name_leave = leave_id.name
                        pr_hour = 0

                if self.time_out >= in_time and self.time_in <= out_time:
                    self.amount_deduc = 0
                    break

                elif self.time_out <= in_time and self.time_in >= out_time:
                    break_time = out_time - in_time
                    break_time = (break_time.total_seconds() / 3600.0)
                    self.total_time = break_time
                    work_hours = self.time_in - self.time_out
                    total_break_time = (work_hours.total_seconds() / 3600.0) - break_time
                    self.amount_deduc = total_break_time * pr_hour
                    break

                elif self.time_out <= in_time and self.time_in <= out_time and self.time_in > in_time:
                    break_time = in_time - self.time_in
                    break_time = (break_time.total_seconds() / 3600.0)
                    self.total_time = break_time
                    work_hours = self.time_in - self.time_out
                    total_break_time = (work_hours.total_seconds() / 3600.0) - break_time
                    self.amount_deduc = total_break_time * pr_hour
                    break

                elif self.time_out > in_time and self.time_out < out_time and self.time_in > out_time:
                    break_time = self.time_out - out_time
                    break_time = (break_time.total_seconds() / 3600.0)
                    self.total_time = break_time
                    work_hours = self.time_in - self.time_out
                    total_break_time = (work_hours.total_seconds() / 3600.0) - break_time
                    self.amount_deduc = total_break_time * pr_hour
                    break

                else:
                    work_hours = self.time_in - self.time_out
                    total_break_time = (work_hours.total_seconds() / 3600.0)
                    self.total_time = total_break_time
                    self.amount_deduc = total_break_time * pr_hour
                    break


            else:
                if self.time_out >= in_time and self.time_in <= out_time:
                    time_deduction = 0

                elif self.time_out <= in_time and self.time_in >= out_time:
                    break_time = out_time - in_time
                    break_time = (break_time.total_seconds() / 3600.0)
                    self.total_time = break_time
                    work_hours = self.time_in - self.time_out
                    total_break_time = (work_hours.total_seconds() / 3600.0) - break_time
                    time_deduction = total_break_time


                elif self.time_out <= in_time and self.time_in <= out_time and self.time_in > in_time:
                    break_time = in_time - self.time_in
                    break_time = (break_time.total_seconds() / 3600.0)
                    self.total_time = break_time
                    work_hours = self.time_in - self.time_out
                    total_break_time = (work_hours.total_seconds() / 3600.0) - break_time
                    time_deduction = total_break_time


                elif self.time_out > in_time and self.time_out < out_time and self.time_in > out_time:
                    break_time = self.time_out - out_time
                    break_time = (break_time.total_seconds() / 3600.0)
                    self.total_time = break_time
                    work_hours = self.time_in - self.time_out
                    total_break_time = (work_hours.total_seconds() / 3600.0) - break_time
                    time_deduction = total_break_time


                else:
                    work_hours = self.time_in - self.time_out
                    total_break_time = (work_hours.total_seconds() / 3600.0)
                    self.total_time = total_break_time
                    time_deduction = total_break_time


                if total_leave >= time_deduction and time_deduction != 0:
                    id = self.env['hr.leave'].create({
                        'employee_id': self.name.id,
                        'date_from': self.date,
                        'date_to': self.date,
                        'request_date_from': self.date,
                        'request_date_to': self.date,
                        'holiday_status_id': leave_id.id,
                        'number_of_days': time_deduction,
                        'name': 'Late Deduction',

                    })
                    print(id)

                    # id.action_validate()
                    self.amount_deduc = 0
                    break






   