from odoo import models, fields, api
from datetime import date, timedelta, datetime
from pytz import timezone

class AttendanceSummaryReport(models.TransientModel):
    _name = 'att.summary.report'
    _description = 'Attendance Summary Report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    show_presents = fields.Boolean(string='Show Presents', default=False)
    show_leaves = fields.Boolean(string='Show Leaves', default=False)
    show_absents = fields.Boolean(string='Show Absents', default=False)
    show_lates = fields.Boolean(string='Show Lates', default=False)
    show_hd = fields.Boolean(string='Show Half Days', default=False)
    show_schedule_hours = fields.Boolean(string='Show Schedule Hours', default=False)
    show_worked_hours = fields.Boolean(string='Show Worked Hourse', default=False)
    show_extra_time = fields.Boolean(string='Show Short/Excess Time', default=False)

    filter_by = fields.Selection([
        ('employee', 'Employee'),
        ('department', 'Department'),
        ('company', 'Company'),
        ('team', 'Team'),
    ], string='Filter By')

    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.company, readonly=True)

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    department_ids = fields.Many2many('hr.department', string='Departments')
    team_ids = fields.Many2many('x_team', string='Team')

    def _get_extra_or_short_time(self, emp, date_from, date_to):
        extra_time = 0.0
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', emp.id),
            ('check_in', '>=', date_from),
            ('check_in', '<=', date_to),
        ])

        if not attendances:
            return 0.0

        emp_tz = emp.tz or self.env.user.tz or 'UTC'

        for att in attendances:

            if not att.check_in or not att.check_out:
                continue

            check_in = fields.Datetime.context_timestamp(emp, att.check_in)
            check_out = fields.Datetime.context_timestamp(emp, att.check_out)

            weekday = str(check_in.weekday())
            day_lines = emp.resource_calendar_id.attendance_ids.filtered(
                lambda l: l.dayofweek == weekday
            )

            if not day_lines:
                continue

            scheduled_start_hour = min(line.hour_from for line in day_lines)
            scheduled_end_hour = max(line.hour_to for line in day_lines)

            day_start = check_in.replace(hour=0, minute=0, second=0, microsecond=0)
            scheduled_start = day_start + timedelta(
                hours=scheduled_start_hour
            )
            scheduled_end = day_start + timedelta(
                hours=min(scheduled_end_hour, 23.9999)
            )

            diff_start = (check_in - scheduled_start).total_seconds() / 3600.0
            diff_end = (check_out - scheduled_end).total_seconds() / 3600.0

            extra_time += diff_end - diff_start

        return round(extra_time, 2)

    def _float_to_hours(self, float_hours):
        total_seconds = int(round(abs(float_hours) * 3600))
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        if float_hours < 0:
            time_str = f"-{time_str}"
        return time_str

    def _get_schedule_days(self, calendar, date_from, date_to):
        if not calendar:
            return 0

        work_days = set()
        for line in calendar.attendance_ids:
            work_days.add(int(line.dayofweek))

        total_days = 0
        current_date = date_from

        while current_date <= date_to:
            if current_date.weekday() in work_days:
                total_days += 1
            current_date += timedelta(days=1)

        return total_days

    def _get_scheduled_hours(self, calendar, date_from, date_to):
        if not calendar:
            return 0.0

        total_hours = 0.0
        current_date = date_from

        while current_date <= date_to:
            weekday = str(current_date.weekday())

            day_lines = calendar.attendance_ids.filtered(
                lambda a: a.dayofweek == weekday
            )

            for line in day_lines:
                total_hours += (line.hour_to - line.hour_from)

            current_date += timedelta(days=1)

        return round(total_hours, 2)

    def action_print_report(self):
        date_from = self.date_from
        date_to = self.date_to

        domain = [
            ('check_in', '>=', date_from),
            ('check_in', '<=', date_to),
        ]

        if self.filter_by == 'company' and self.company_id:
            domain.append(('employee_id.company_id', '=', self.company_id.id))

        elif self.filter_by == 'employee' and self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))

        elif self.filter_by == 'department' and self.department_ids:
            domain.append(('employee_id.department_id', 'in', self.department_ids.ids))

        elif self.filter_by == 'team' and self.team_ids:
            domain.append(('employee_id.x_studio_team', 'in', self.team_ids.ids))

        attendances = self.env['hr.attendance'].search(domain)

        emp_att_map = {}
        for att in attendances:
            emp_att_map.setdefault(att.employee_id, []).append(att)

        report_data = []

        for emp, emp_atts in emp_att_map.items():
            present_days = len(set(att.check_in.date() for att in emp_atts))


            half_days = 0
            counted_dates = set()

            for att in emp_atts:
                if not att.check_in:
                    continue

                check_in = fields.Datetime.context_timestamp(emp, att.check_in)
                print(check_in)
                att_date = check_in.date()
                weekday = str(att_date.weekday())

                is_scheduled_day = emp.resource_calendar_id and emp.resource_calendar_id.attendance_ids.filtered(
                    lambda a: a.dayofweek == weekday
                )

                if att_date in counted_dates:
                    continue

                if is_scheduled_day and check_in.hour >= 11 or is_scheduled_day and att.worked_hours < 4.5:
                    half_days += 1
                    counted_dates.add(att_date)

            schedule_days = 0
            if emp.resource_calendar_id:
                schedule_days = self._get_schedule_days(
                    emp.resource_calendar_id,
                    date_from,
                    date_to
                )
            ghazetted_days = 0

            if emp.resource_calendar_id:
                ghazetted_leaves = self.env['hr.leave'].search([
                    ('employee_id', '=', emp.id),
                    ('state', 'in', ['validate', 'validate1']),
                    ('holiday_status_id.name', 'ilike', 'ghazetted'),
                    ('request_date_from', '<=', date_to),
                    ('request_date_to', '>=', date_from),
                ])

                for leave in ghazetted_leaves:
                    current = max(leave.request_date_from, date_from)
                    end = min(leave.request_date_to, date_to)

                    while current <= end:
                        weekday = str(current.weekday())
                        is_scheduled = emp.resource_calendar_id.attendance_ids.filtered(
                            lambda a: a.dayofweek == weekday
                        )
                        if is_scheduled:
                            ghazetted_days += 1
                        current += timedelta(days=1)

            schedule_days -= ghazetted_days
            schedule_days = max(schedule_days, 0)

            absent_days = self.env['absent.deduction.lines'].search_count([
                ('employee_id', '=', emp.id),
                ('absent_date', '>=', date_from),
                ('absent_date', '<=', date_to),
            ])

            late_days = self.env['late.deduction.lines'].search_count([
                ('employee_id', '=', emp.id),
                ('check_in', '>=', date_from),
                ('check_out', '<=', date_to),
                ('exemption', '=', False),
            ])

            late_deduction_days = late_days

            leaves = self.env['hr.leave'].search([
                ('employee_id', '=', emp.id),
                ('state', 'in', ['validate','validate1']),
                ('request_date_from', '<=', date_to),
                ('request_date_to', '>=', date_from),
                ('holiday_status_id', '!=', ['Unpaid','Ghazetted Holiday']),
            ])

            leave_days = 0
            for leave in leaves:
                leave_start = max(leave.request_date_from, date_from)
                leave_end = min(leave.request_date_to, date_to)

                current_date = leave_start
                while current_date <= leave_end:
                    if current_date.weekday() < 5:
                        leave_days += 1
                    current_date += timedelta(days=1)

            # half_day_count = self.env['hr.leave'].search_count([
            #     ('employee_id', '=', emp.id),
            #     ('state', '=', 'validate'),
            #     ('request_unit_half', '=', True),
            #     ('holiday_status_id.unpaid', '=', True),
            #     ('request_date_from', '<=', date_to),
            #     ('request_date_to', '>=', date_from),
            # ])
            #
            # half_days = half_day_count

            worked_hours = sum(att.worked_hours for att in emp_atts)
            scheduled_hours = self._get_scheduled_hours(
                emp.resource_calendar_id,
                date_from,
                date_to
            )
            paid_leaves = self.env['hr.leave'].search([
                ('employee_id', '=', emp.id),
                ('state', 'in', ['validate','validate1']),
                ('request_date_from', '<=', date_to),
                ('request_date_to', '>=', date_from),
                ('holiday_status_id', '!=', 'Unpaid'),
            ])
            leave_hours = 0.0

            for leave in paid_leaves:
                leave_start = max(leave.request_date_from, date_from)
                leave_end = min(leave.request_date_to, date_to)

                current_date = leave_start
                while current_date <= leave_end:
                    weekday = str(current_date.weekday())
                    is_working_day = emp.resource_calendar_id.attendance_ids.filtered(
                        lambda a: a.dayofweek == weekday
                    )
                    if is_working_day:
                        leave_hours += emp.resource_calendar_id.hours_per_day

                    current_date += timedelta(days=1)

            day_hours = 0.0

            if emp.resource_calendar_id:
                attendance_lines = emp.resource_calendar_id.attendance_ids
                if attendance_lines:
                    day_hours = sum(
                        line.hour_to - line.hour_from
                        for line in attendance_lines
                    ) / len(set(attendance_lines.mapped('dayofweek')))

            # leave_hours = sum(l.number_of_days * emp.resource_calendar_id.hours_per_day for l in paid_leaves)
            half_day_hours = (day_hours / 2) * half_days
            scheduled_hours -= half_day_hours
            scheduled_hours = max(scheduled_hours, 0)
            scheduled_hours -= leave_hours
            scheduled_hours = max(scheduled_hours, 0)

            # extra_time = self._get_extra_or_short_time(emp,date_from,date_to)
            extra_time = worked_hours - scheduled_hours

            report_data.append({
                'employee_id': emp.id,
                'employee_name': emp.name,
                'department': emp.department_id.name,
                'team': emp.x_studio_team.x_name,
                'designation': emp.job_id.name,
                'code': emp.barcode,
                'status': 'Active',
                'schedule_days': schedule_days,
                'present_days': present_days,
                'leave_days': leave_days,
                'half_days': half_days,
                'absent_days': absent_days,
                'late_days': late_deduction_days,
                'scheduled_hours': self._float_to_hours(scheduled_hours),
                'worked_hours': self._float_to_hours(worked_hours),
                'extra_hours': self._float_to_hours(extra_time),
            })

        final_report = {
            'employee_lines': report_data,
            'period': f"From {self.date_from} to {self.date_to}",
            'show_presents': self.show_presents,
            'show_leaves': self.show_leaves,
            'show_absents': self.show_absents,
            'show_lates': self.show_lates,
            'show_hd': self.show_hd,
            'show_schedule_hours': self.show_schedule_hours,
            'show_worked_hours': self.show_worked_hours,
            'show_extra_time': self.show_extra_time,
        }
        return self.env.ref('attendance_summary_report.action_att_summary_report').report_action(self, data=final_report)


