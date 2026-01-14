from odoo import models, fields, api
from datetime import timedelta, datetime, time
import pytz


class EmployeeScheduleReport(models.TransientModel):
    _name = 'employee.schedule.report'
    _description = 'Employee Schedule Report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    filter_by = fields.Selection([
        ('employee', 'Employee'),
        ('team', 'Team'),
        ('manager', 'Manager'),
    ], string='Filter By')

    team_ids = fields.Many2many('x_team', string='Team')
    employee_id = fields.Many2many('hr.employee', 'employee_schedule_report_employee_rel', string='Employee')
    manager_ids = fields.Many2many('hr.employee', 'employee_schedule_report_manager_rel', string='Managers')

    @api.onchange('filter_by')
    def _onchange_filter_by(self):
        if self.filter_by == 'manager':
            managers = self.env['hr.employee'].search([
                ('id', 'in', self.env['hr.employee'].search([]).mapped('parent_id').ids)
            ])
            self.manager_ids = managers

    def _float_to_time(self, hour):
        if hour is None or hour == '-' or hour is False:
            return '-'
        hours = int(hour)
        minutes = int(round((hour - hours) * 60))
        return f"{hours:02d}:{minutes:02d}"

    def print_report(self):
        result_lines = []
        employees_data = []

        if self.filter_by == 'team' and self.team_ids:
            employees = self.env['hr.employee'].search([('x_studio_team', 'in', self.team_ids.ids)])
        elif self.filter_by == 'manager' and self.manager_ids:
            employees = self.manager_ids
        else:
            employees = self.employee_id

        for emp in employees:

            emp_lines = []

            totals = {
                'scheduled_hours': 0.0,
                'worked_hours': 0.0,
                'scheduled_days': 0,
                'present_days': 0,
                'leave_days': 0,
                'half_days': 0,
                'full_day_leaves': 0,
                'absent_days': 0,
                'late_days': 0,
            }
            emp_tz = pytz.timezone(emp.tz or self.env.user.tz or 'UTC')

            current_date = self.date_from
            day_hours = 0.0
            while current_date <= self.date_to:

                scheduled_in = False
                scheduled_out = False
                is_half_day = False

                calendar = emp.resource_calendar_id
                if calendar:
                    weekday = str(current_date.weekday())
                    attendances = calendar.attendance_ids.filtered(
                        lambda a: a.dayofweek == weekday
                    )
                    if attendances:
                        scheduled_in = min(attendances.mapped('hour_from'))
                        scheduled_out = max(attendances.mapped('hour_to'))

                if scheduled_in is not False and scheduled_out is not False:
                    totals['scheduled_days'] += 1
                    totals['scheduled_hours'] += (scheduled_out - scheduled_in)
                    day_hours = scheduled_out - scheduled_in

                date_start = datetime.combine(current_date, time.min)
                date_end = datetime.combine(current_date, time.max)

                attendance = self.env['hr.attendance'].search([
                    ('employee_id', '=', emp.id),
                    ('check_in', '>=', date_start),
                    ('check_in', '<=', date_end),
                ], limit=1)

                check_in = '-'
                check_out = '-'

                if attendance and attendance.check_in:
                    ci = fields.Datetime.from_string(attendance.check_in)
                    if ci.tzinfo is None:
                        ci = pytz.UTC.localize(ci)
                    check_in = ci.astimezone(emp_tz).strftime('%I:%M:%S %p')

                if attendance and attendance.check_out:
                    co = fields.Datetime.from_string(attendance.check_out)
                    if co.tzinfo is None:
                        co = pytz.UTC.localize(co)
                    check_out = co.astimezone(emp_tz).strftime('%I:%M:%S %p')

                worked_time = attendance.worked_hours if attendance else 0.0

                remarks = 'Absent'

                if attendance:
                    remarks = 'Present'
                    totals['present_days'] += 1
                    totals['worked_hours'] += worked_time

                    if scheduled_in:
                        scheduled_dt = emp_tz.localize(
                            datetime.combine(
                                current_date,
                                time(
                                    hour=int(scheduled_in),
                                    minute=int((scheduled_in % 1) * 60)
                                )
                            )
                        )
                        actual_ci = fields.Datetime.from_string(attendance.check_in)
                        if actual_ci.tzinfo is None:
                            actual_ci = pytz.UTC.localize(actual_ci)
                        actual_ci = actual_ci.astimezone(emp_tz)

                        if worked_time < 4:
                            remarks = 'Present, Half Day'
                            is_half_day = True


                        elif scheduled_in and actual_ci.time() > time(11, 0):
                            remarks = 'Present, Half Day'
                            is_half_day = True

                        elif actual_ci >= scheduled_dt + timedelta(minutes=11):

                            late_exempt = self.env['late.deduction.lines'].search([
                                ('employee_id', '=', emp.id),
                                ('check_in', '=', current_date),
                                ('exemption', '=', True)
                            ], limit=1)

                            if late_exempt:
                                remarks = 'Present, Late Exempted'
                            else:
                                remarks = 'Present, Late'
                                totals['late_days'] += 1
                            # remarks = 'Present, Late'
                            # totals['late_days'] += 1

                leave = self.env['hr.leave'].search([
                    ('employee_id', '=', emp.id),
                    ('state', 'in', ['validate', 'validate1']),
                    ('request_date_from', '<=', current_date),
                    ('request_date_to', '>=', current_date),
                    ('holiday_status_id.name', '!=', 'Unpaid'),
                ], limit=1)

                if leave:
                    if scheduled_in and scheduled_out:
                        if leave.request_unit_half:
                            remarks = 'Half Day Leave'
                            is_half_day = True
                        else:
                            if leave.holiday_status_id.name.lower() == 'ghazetted holiday':
                                remarks = leave.holiday_status_id.name
                                totals['scheduled_days'] -= 1
                                totals['scheduled_hours'] -= day_hours
                            else:
                                totals['leave_days'] += 1
                                totals['full_day_leaves'] += 1
                                remarks = leave.holiday_status_id.name

                if is_half_day:
                    totals['half_days'] += 1

                if not scheduled_in and not scheduled_out:
                    remarks = 'Holiday'
                    worked_time = 0.0

                if remarks == 'Absent':
                    totals['absent_days'] += 1

                schedule_name = calendar.name if calendar else 'No Schedule'

                line_data = {
                    'employee': emp.name,
                    'dept': emp.department_id.name if emp.department_id else '-',
                    'Job': emp.job_id.name if emp.job_id else '-',
                    'code': emp.barcode or '-',
                    'team': emp.x_studio_team.x_name if emp.x_studio_team else '-',
                    'manager': emp.parent_id.name if emp.parent_id else '-',
                    'emp_status': 'Active',
                    'date': current_date.strftime('%d/%m/%Y'),
                    'name': schedule_name,
                    'scheduled_in': self._float_to_time(scheduled_in),
                    'scheduled_out': self._float_to_time(scheduled_out),
                    'check_in': check_in,
                    'check_out': check_out,
                    'worked_time': self._float_to_time(worked_time),
                    'remarks': remarks,
                    'scheduled_days': totals['scheduled_days'],
                    'scheduled_hours': totals['scheduled_hours'],
                    'worked_hours': totals['worked_hours'],
                    'present_days': totals['present_days'],
                    'leave_days': totals['leave_days'],
                    'half_days': totals['half_days'],
                    'full_day_leaves': totals['full_day_leaves'],
                    'absent_days': totals['absent_days'],
                    'lates': totals['late_days'],
                }

                emp_lines.append(line_data)
                current_date += timedelta(days=1)

            totals['scheduled_hours'] -= (
                    (totals['full_day_leaves'] * day_hours) +
                    (totals['half_days'] * (day_hours / 2))
            )
            totals['scheduled_hours'] = max(totals['scheduled_hours'], 0.0)
            employees_data.append({
                'employee_info': emp_lines[0],
                'lines': emp_lines,
                'totals': totals,
            })

        final_data = {
            'employees': employees_data,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'period': f"From {self.date_from} to {self.date_to}",
        }

        return self.env.ref(
            'employee_schedule_report.employee_schedule_report_action'
        ).report_action(self, data=final_data)

    def print_report_xlsx(self):
        result_lines = []
        employees_data = []

        if self.filter_by == 'team' and self.team_ids:
            employees = self.env['hr.employee'].search([('x_studio_team', 'in', self.team_ids.ids)])
        elif self.filter_by == 'manager' and self.manager_ids:
            employees = self.manager_ids

        else:
            employees = self.employee_id

        for emp in employees:

            emp_lines = []

            totals = {
                'scheduled_hours': 0.0,
                'worked_hours': 0.0,
                'scheduled_days': 0,
                'present_days': 0,
                'leave_days': 0,
                'half_days': 0,
                'full_day_leaves': 0,
                'absent_days': 0,
                'late_days': 0,
            }
            emp_tz = pytz.timezone(emp.tz or self.env.user.tz or 'UTC')

            current_date = self.date_from
            day_hours = 0.0
            while current_date <= self.date_to:

                scheduled_in = False
                scheduled_out = False
                is_half_day = False

                calendar = emp.resource_calendar_id
                if calendar:
                    weekday = str(current_date.weekday())
                    attendances = calendar.attendance_ids.filtered(
                        lambda a: a.dayofweek == weekday
                    )
                    if attendances:
                        scheduled_in = min(attendances.mapped('hour_from'))
                        scheduled_out = max(attendances.mapped('hour_to'))

                if scheduled_in is not False and scheduled_out is not False:
                    totals['scheduled_days'] += 1
                    totals['scheduled_hours'] += (scheduled_out - scheduled_in)
                    day_hours = scheduled_out - scheduled_in

                date_start = datetime.combine(current_date, time.min)
                date_end = datetime.combine(current_date, time.max)

                attendance = self.env['hr.attendance'].search([
                    ('employee_id', '=', emp.id),
                    ('check_in', '>=', date_start),
                    ('check_in', '<=', date_end),
                ], limit=1)

                check_in = '-'
                check_out = '-'

                if attendance and attendance.check_in:
                    ci = fields.Datetime.from_string(attendance.check_in)
                    if ci.tzinfo is None:
                        ci = pytz.UTC.localize(ci)
                    check_in = ci.astimezone(emp_tz).strftime('%I:%M:%S %p')

                if attendance and attendance.check_out:
                    co = fields.Datetime.from_string(attendance.check_out)
                    if co.tzinfo is None:
                        co = pytz.UTC.localize(co)
                    check_out = co.astimezone(emp_tz).strftime('%I:%M:%S %p')

                worked_time = attendance.worked_hours if attendance else 0.0

                remarks = 'Absent'

                if attendance:
                    remarks = 'Present'
                    totals['present_days'] += 1
                    totals['worked_hours'] += worked_time

                    if scheduled_in:
                        scheduled_dt = emp_tz.localize(
                            datetime.combine(
                                current_date,
                                time(
                                    hour=int(scheduled_in),
                                    minute=int((scheduled_in % 1) * 60)
                                )
                            )
                        )
                        actual_ci = fields.Datetime.from_string(attendance.check_in)

                        if actual_ci.tzinfo is None:
                            actual_ci = pytz.UTC.localize(actual_ci)
                        actual_ci = actual_ci.astimezone(emp_tz)

                        if worked_time < 4:
                            remarks = 'Present, Half Day'
                            is_half_day = True

                        elif scheduled_in and actual_ci.time() > time(11, 0):
                            remarks = 'Present, Half Day'
                            is_half_day = True

                        elif actual_ci >= scheduled_dt + timedelta(minutes=11):
                            remarks = 'Present, Late'
                            totals['late_days'] += 1

                leave = self.env['hr.leave'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'validate'),
                    ('request_date_from', '<=', current_date),
                    ('request_date_to', '>=', current_date),
                ], limit=1)

                if leave:
                    if leave.request_unit_half:
                        remarks = 'Half Day Leave'
                        is_half_day = True
                    else:
                        if leave.holiday_status_id.name.lower() == 'ghazetted holiday':
                            remarks = leave.holiday_status_id.name
                            totals['scheduled_days'] -= 1
                            totals['scheduled_hours'] -= day_hours
                        else:
                            totals['leave_days'] += 1
                            totals['full_day_leaves'] += 1
                            remarks = leave.holiday_status_id.name

                if is_half_day:
                    totals['half_days'] += 1

                if not scheduled_in and not scheduled_out:
                    remarks = 'Holiday'
                    worked_time = 0.0

                if remarks == 'Absent':
                    totals['absent_days'] += 1

                schedule_name = calendar.name if calendar else 'No Schedule'

                line_data = {
                    'employee': emp.name,
                    'dept': emp.department_id.name if emp.department_id else '-',
                    'Job': emp.job_id.name if emp.job_id else '-',
                    'code': emp.barcode or '-',
                    'team': emp.x_studio_team.x_name if emp.x_studio_team else '-',
                    'manager': emp.parent_id.name if emp.parent_id else '-',
                    'emp_status': 'Active',
                    'date': current_date.strftime('%d/%m/%Y'),
                    'name': schedule_name,
                    'scheduled_in': self._float_to_time(scheduled_in),
                    'scheduled_out': self._float_to_time(scheduled_out),
                    'check_in': check_in,
                    'check_out': check_out,
                    'worked_time': self._float_to_time(worked_time),
                    'remarks': remarks,
                    'scheduled_days': totals['scheduled_days'],
                    'scheduled_hours': self._float_to_time(totals['scheduled_hours']),
                    'worked_hours': self._float_to_time(totals['worked_hours']),
                    'present_days': totals['present_days'],
                    'leave_days': totals['leave_days'],
                    'half_days': totals['half_days'],
                    'full_day_leaves': totals['full_day_leaves'],
                    'absent_days': totals['absent_days'],
                    'lates': totals['late_days'],
                }

                emp_lines.append(line_data)
                current_date += timedelta(days=1)

            totals['scheduled_hours'] -= (
                    (totals['full_day_leaves'] * day_hours) +
                    (totals['half_days'] * (day_hours / 2))
            )
            totals['scheduled_hours'] = max(totals['scheduled_hours'], 0.0)
            employees_data.append({
                'employee_info': emp_lines[0],
                'lines': emp_lines,
                'totals': totals,
            })

        final_data = {
            'employees': employees_data,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'period': f"From {self.date_from} to {self.date_to}",
        }

        return self.env.ref(
            'employee_schedule_report.employee_schedule_report_action_xlsx'
        ).report_action(self, data=final_data)
