from odoo import models, fields, api
from datetime import date, timedelta, datetime
from pytz import timezone
import calendar

class AttendanceSummaryReport(models.TransientModel):
    _name = 'att.analysis.report'
    _description = 'Attendance Analysis Report'

    date_from = fields.Date(string='Date From', required=True, default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(string='Date To', required=True, default=lambda self: date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1]))
    minimum_count = fields.Integer(string='Minimum Count')
    maximum_count = fields.Integer(string='Maximum Count')
    filter_by = fields.Selection([
        ('employee', 'Employees'),
        ('job', 'Jobs'),
        ('team', 'Teams'),
    ], string='Filter By', required=True)

    report_of = fields.Selection([
        ('leaves', 'Leaves'),
        ('lates', 'Lates'),
        ('absences', 'Absences'),
    ], string='Report Of', required=True)

    sorting_method = fields.Selection([
        ('ascending', 'Ascending'),
        ('descending', 'Descending'),
    ], string='Sorting', default='ascending')

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    job_ids = fields.Many2many('hr.job', string='Job')
    team_ids = fields.Many2many('x_team', string='Team')
    show_email = fields.Boolean(string='Show Email')

    def action_print_attendance_report(self):
        date_from = self.date_from
        date_to = self.date_to

        if self.filter_by == 'employee' and self.employee_ids:
            employees = self.employee_ids
        elif self.filter_by == 'job' and self.job_ids:
            employees = self.env['hr.employee'].search([('job_id', 'in', self.job_ids.ids)])
        elif self.filter_by == 'team' and self.team_ids:
            employees = self.env['hr.employee'].search([('x_studio_team', 'in', self.team_ids.ids)])
        else:
            employees = self.env['hr.employee'].search([])

        report_data = []

        for emp in employees:
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

            late_deduction_days = max(0, late_days - 2)

            leaves = self.env['hr.leave'].search([
                ('employee_id', '=', emp.id),
                ('state', '=', 'validate'),
                ('request_date_from', '<=', date_to),
                ('request_date_to', '>=', date_from),
                ('holiday_status_id', 'not in', ['Unpaid', 'Ghazatted Holiday']),
                ('request_unit_half', '=', False),
                ('state', '=', 'validate'),
            ])

            # leave_days = sum(leaves.mapped('number_of_days'))
            leave_days = 0
            for leave in leaves:
                leave_start = max(leave.request_date_from, date_from)
                leave_end = min(leave.request_date_to, date_to)

                current_date = leave_start
                while current_date <= leave_end:
                    if current_date.weekday() < 5:
                        leave_days += 1
                    current_date += timedelta(days=1)
                # if leave_start <= leave_end:
                #     leave_days += (leave_end - leave_start).days + 1

            half_leaves = self.env['hr.leave'].search_count([
                ('employee_id', '=', emp.id),
                ('state', '=', 'validate'),
                ('request_date_from', '<=', date_to),
                ('request_date_to', '>=', date_from),
                ('holiday_status_id', '!=', 'Unpaid'),
                ('request_unit_half', '=', True),
                ('state', '=', 'validate'),
            ])
            total_half_days = half_leaves / 2

            if self.report_of == 'lates':
                value_to_check = late_deduction_days
            elif self.report_of == 'absences':
                value_to_check = absent_days
            elif self.report_of == 'leaves':
                value_to_check = leave_days + total_half_days
            else:
                value_to_check = 0

            if self.minimum_count and value_to_check <= self.minimum_count:
                continue
            if self.maximum_count and value_to_check >= self.maximum_count:
                continue

            report_data.append({
                'email': emp.work_email,
                'employee_name': emp.name,
                'team': emp.x_studio_team.x_name,
                'code': emp.barcode,
                'manager': emp.parent_id.name,
                'designation': emp.job_id.name,
                'absent_days': absent_days,
                'leave_days': leave_days + total_half_days,
                'late_days': late_deduction_days,
            })

        filtered_report_data = []

        for line in report_data:
            if self.report_of == 'lates' and line['late_days'] > 0:
                filtered_report_data.append(line)
            elif self.report_of == 'absences' and line['absent_days'] > 0:
                filtered_report_data.append(line)
            elif self.report_of == 'leaves' and line['leave_days'] > 0:
                filtered_report_data.append(line)

        if self.report_of == 'lates':
            sort_field = 'late_days'
        elif self.report_of == 'absences':
            sort_field = 'absent_days'
        elif self.report_of == 'leaves':
            sort_field = 'leave_days'
        else:
            sort_field = None

        if sort_field:
            filtered_report_data = sorted(
                filtered_report_data,
                key=lambda x: x[sort_field],
                reverse=(self.sorting_method == 'descending')
            )

        final_report = {
            'employee_lines': filtered_report_data,
            'period': f"From {self.date_from.strftime('%d %b %Y')} to {self.date_to.strftime('%d %b %Y')}",
            'report_of': self.report_of,
            'show_email': self.show_email,
        }
        return self.env.ref('att_analysis_report.action_att_analysis_report').report_action(self, data=final_report)


    def action_print_attendance_report_xlsx(self):
        date_from = self.date_from
        date_to = self.date_to

        if self.filter_by == 'employee' and self.employee_ids:
            employees = self.employee_ids
        elif self.filter_by == 'job' and self.job_ids:
            employees = self.env['hr.employee'].search([('job_id', 'in', self.job_ids.ids)])
        elif self.filter_by == 'team' and self.team_ids:
            employees = self.env['hr.employee'].search([('x_studio_team', 'in', self.team_ids.ids)])
        else:
            employees = self.env['hr.employee'].search([])

        report_data = []

        for emp in employees:
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

            late_deduction_days = max(0, late_days - 2)

            leaves = self.env['hr.leave'].search([
                ('employee_id', '=', emp.id),
                ('state', '=', 'validate'),
                ('request_date_from', '<=', date_to),
                ('request_date_to', '>=', date_from),
                ('holiday_status_id', 'not in', ['Unpaid', 'Ghazatted Holiday']),
                ('request_unit_half', '=', False),
                ('state', '=', 'validate'),
            ])

            # leave_days = sum(leaves.mapped('number_of_days'))
            leave_days = 0
            for leave in leaves:
                leave_start = max(leave.request_date_from, date_from)
                leave_end = min(leave.request_date_to, date_to)

                current_date = leave_start
                while current_date <= leave_end:
                    if current_date.weekday() < 5:
                        leave_days += 1
                    current_date += timedelta(days=1)

            half_leaves = self.env['hr.leave'].search_count([
                ('employee_id', '=', emp.id),
                ('state', '=', 'validate'),
                ('request_date_from', '<=', date_to),
                ('request_date_to', '>=', date_from),
                ('holiday_status_id', '!=', 'Unpaid'),
                ('request_unit_half', '=', True),
                ('state', '=', 'validate'),
            ])
            total_half_days = half_leaves / 2

            if self.report_of == 'lates':
                value_to_check = late_deduction_days
            elif self.report_of == 'absences':
                value_to_check = absent_days
            elif self.report_of == 'leaves':
                value_to_check = leave_days + total_half_days
            else:
                value_to_check = 0

            if self.minimum_count and value_to_check <= self.minimum_count:
                continue
            if self.maximum_count and value_to_check >= self.maximum_count:
                continue

            report_data.append({
                'email': emp.work_email,
                'employee_name': emp.name,
                'team': emp.x_studio_team.x_name,
                'code': emp.barcode,
                'manager': emp.parent_id.name,
                'designation': emp.job_id.name,
                'absent_days': absent_days,
                'leave_days': leave_days + total_half_days,
                'late_days': late_deduction_days,
            })

        filtered_report_data = []

        for line in report_data:
            if self.report_of == 'lates' and line['late_days'] > 0:
                filtered_report_data.append(line)
            elif self.report_of == 'absences' and line['absent_days'] > 0:
                filtered_report_data.append(line)
            elif self.report_of == 'leaves' and line['leave_days'] > 0:
                filtered_report_data.append(line)

        if self.report_of == 'lates':
            sort_field = 'late_days'
        elif self.report_of == 'absences':
            sort_field = 'absent_days'
        elif self.report_of == 'leaves':
            sort_field = 'leave_days'
        else:
            sort_field = None

        if sort_field:
            filtered_report_data = sorted(
                filtered_report_data,
                key=lambda x: x[sort_field],
                reverse=(self.sorting_method == 'descending')
            )

        final_report = {
            'employee_lines': filtered_report_data,
            'period': f"From {self.date_from.strftime('%d %b %Y')} to {self.date_to.strftime('%d %b %Y')}",
            'report_of': self.report_of,
            'show_email': self.show_email,
        }
        return self.env.ref('att_analysis_report.action_att_analysis_report_xlsx').report_action(self, data=final_report)


