from odoo import models, fields, api
from datetime import date, timedelta, datetime
from pytz import timezone
import calendar

class EmployeeActivityReport(models.TransientModel):
    _name = 'emp.activity.report'
    _description = 'Employee Activity Report'

    plan_id = fields.Many2one('mail.activity.plan', string='Plan', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    # emp_ids = fields.Many2many('hr.employee',compute='get_planned_employees', string='Employees')

    def action_print_activity_report(self):
        today = fields.Date.today()

        if self.employee_ids:
            employees = self.employee_ids
        else:
            employees = self.env['hr.employee'].search([])

        # template_ids = self.plan_id.template_ids.ids
        plan_activity_type_ids = self.plan_id.template_ids.mapped('activity_type_id').ids
        employee_dict = {}

        for employee in employees:

            activities = self.env['mail.activity'].with_context(active_test=False).search([
                ('res_model', '=', 'hr.employee'),
                ('res_id', '=', employee.id),
                ('activity_type_id', 'in', plan_activity_type_ids),
            ])
            for act in activities:

                if act.activity_type_id.id not in plan_activity_type_ids:
                    continue

                if act.state == 'done':
                    status = 'Done'
                elif act.date_deadline < today:
                    status = 'Overdue'
                elif act.date_deadline == today:
                    status = 'Today'
                else:
                    status = 'Planned'

                if employee.id not in employee_dict:
                    employee_dict[employee.id] = {
                        'employee_name': employee.name,
                        'department': employee.department_id.name if employee.department_id else '',
                        'team': employee.x_studio_team.x_name if employee.x_studio_team else '',
                        'designation': employee.job_id.name if employee.job_id else '',
                        'activities': []
                    }

                employee_dict[employee.id]['activities'].append({
                    'summary': act.summary,
                    'due_date': act.date_deadline.strftime('%d %b %y') if act.date_deadline else '',
                    'status': status,
                    'done_date': act.date_done.strftime('%d %b %y') if act.state == 'done' and act.date_done else '',
                })

        # activities = self.env['mail.activity'].search([
        #     ('activity_type_id', 'in', template_ids),
        #     ('res_model', '=', 'hr.employee'),
        #     ('res_id', 'in', employees.ids),
        # ])

        # employee_dict = {}
        #
        #
        # for act in activities:
        #     print(act.display_name)
        #     employee = self.env['hr.employee'].browse(act.res_id)
        #
        #     if act.state == 'done':
        #         status = 'Done'
        #     elif act.date_deadline < today:
        #         status = 'Overdue'
        #     elif act.date_deadline == today:
        #         status = 'Today'
        #     else:
        #         status = 'Planned'
        #
        #     if employee.id not in employee_dict:
        #         employee_dict[employee.id] = {
        #             'employee_name': employee.name,
        #             'department': employee.department_id.name if employee.department_id else '',
        #             'team': employee.x_studio_team.x_name if employee.x_studio_team else '',
        #             'designation': employee.job_id.name if employee.job_id else '',
        #             'activities': []
        #         }
        #
        #     employee_dict[employee.id]['activities'].append({
        #         'summary': act.summary,
        #         'due_date': act.date_deadline.strftime('%d %b %y'),
        #         'status': status,
        #     })

        report_data = list(employee_dict.values())

        final_report_data = {
            'plan': self.plan_id.name,
            'records': report_data,
        }

        return self.env.ref('employee_activity_report.action_employee_activity_report').report_action(self, data=final_report_data)


