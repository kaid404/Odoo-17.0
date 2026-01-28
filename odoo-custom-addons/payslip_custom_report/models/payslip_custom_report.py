from odoo import models, fields, api

class PayslipCustomReport(models.Model):
    _name = 'payslip.custom.report'
    _description = 'Payslip Custom Report'

    filter_by = fields.Selection([('employees', 'Employees'),('team', 'Team'),('company', 'Company')],string='Filter By',required=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    team_ids = fields.Many2many('x_team', string='Teams')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    def print_report(self):
        date_from = self.date_from
        date_to = self.date_to

        domain = [
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
        ]

        if self.filter_by == 'company' and self.company_id:
            domain.append(('employee_id.company_id', '=', self.company_id.id))

        elif self.filter_by == 'employees' and self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))


        elif self.filter_by == 'team' and self.team_ids:
            domain.append(('employee_id.x_studio_team', 'in', self.team_ids.ids))

        payslips = self.env['hr.payslip'].search(domain)

        report_data = []

        for slip in payslips:
            earnings = []
            deductions = []
            net_amount = 0

            for line in slip.line_ids:
                if line.total == 0:
                    continue

                line_data = {
                    'name': line.name,
                    'amount': round(abs(line.total)),
                }

                if line.category_id.code in ('BASIC', 'ALW'):
                    earnings.append(line_data)

                elif line.category_id.code == 'DED':
                    deductions.append(line_data)
                elif line.category_id.code == 'NET':
                    net_amount = round(line.total)

            emp = slip.employee_id
            currency = slip.company_id.currency_id
            net_in_words = currency.amount_to_text(net_amount) if currency else ''

            report_data.append({
                'code': emp.barcode or '',
                'name': emp.name or '',
                'team': emp.x_studio_team.x_name if emp.x_studio_team else '',
                'designation': emp.job_id.name if emp.job_id else '',
                'joining_date': emp.contract_id.date_start or '',
                'department': emp.department_id.name if emp.department_id else '',
                'cnic': emp.identification_id or '',
                'monthly_salary': emp.contract_id.wage if emp.contract_id else 0.0,
                'earnings': earnings,
                'deductions': deductions,
                'net': net_amount,
                'net_in_words': net_in_words,
                'report_currency': slip.company_id.currency_id,
            })

        final_report = {
            'payslips': report_data
        }


        return self.env.ref('payslip_custom_report.action_payslip_custom_report').report_action(self, data=final_report)
