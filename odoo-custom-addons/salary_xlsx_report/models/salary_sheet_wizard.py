from odoo import models, fields

class SalarySheetWizard(models.TransientModel):
    _name = 'salary.sheet.wizard'
    _description = 'Salary Sheet Wizard'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    def print_button(self):
        domain = [
            ('date_from','>=', self.date_from),
            ('date_to','<=', self.date_to),
        ]
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))

        payslips = self.env['hr.payslip'].search(domain)

        final_data = {
            'payslips': list(payslips.ids)
        }


        return self.env.ref('salary_xlsx_report.action_salary_sheet_xlsx_report').report_action(self, data=final_data)
