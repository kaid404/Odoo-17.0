from odoo import _, api, fields, models
from calendar import month_name
from dateutil.relativedelta import relativedelta
from datetime import datetime


class EmpContributionLoanDetails(models.TransientModel):
    _name = 'emp.contribution.loan.details'

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    employee_ids = fields.Many2many('hr.employee', string="Employee Name")

    def contribution_loan_details_report(self):
        record_list = []

        from_month = month_name[self.from_date.month]
        from_year = self.from_date.year
        to_month = month_name[self.to_date.month]
        to_year = self.to_date.year

        loan_domain = [
            ('request_date', '>=', self.from_date),
            ('request_date', '<=', self.to_date),
        ]
        if self.employee_ids:
            loan_domain.append(('employee_id', 'in', self.employee_ids.ids))

        loan_reqs = self.env['hr.advance.salary'].search(loan_domain, order="employee_id ASC")

        for loan in loan_reqs:
            payslip_lines = {}
            remaining_balance = loan.request_amount  # Initialize remaining balance with the loan amount
            remaining_installments = loan.duration_month  # Initialize remaining installments

            loan_number = loan.name
            employee_name = loan.employee_id.name
            date_birth = loan.employee_id.birthday
            employee_code = loan.employee_id.barcode
            joining = loan.employee_id.contract_id.date_start
            emp_company = loan.employee_id.emp_company_id.name
            appointment = loan.employee_id.contract_id.date_start
            father_name = 'Father name'
            department = loan.employee_id.department_id.name
            designation = loan.employee_id.job_id.name
            employee_type = loan.employee_id.work_location_id.name
            grade = 'Grade ---'
            gross_pay = 0
            basic_pay = 0
            return_mode = f'Monthly Installment, {loan.deduction_amount:.2f}'
            deduction = loan.deduction_amount
            installments = loan.duration_month
            required_amount = loan.request_amount
            remarks = loan.reason
            request_date = loan.payment_start_date
            paid = loan.amount_paid
            balance = loan.amount_to_pay
            pf_emp = loan.employee_id.pf_employee_amount
            pf_emper = loan.employee_id.pf_employer_amount

             # Calculate the service duration
            contract_end_date = loan.employee_id.contract_id.date_end or datetime.today()
            service_duration_str = relativedelta(contract_end_date, joining)
            service_duration = f"{service_duration_str.years} years {service_duration_str.months} months {service_duration_str.days} days"

            sum_pf = loan.employee_id.total_amount
            lum_sum = 0
            write_off = 0
           
            salary = self.env['hr.payslip'].search([
                ('employee_id', '=', loan.employee_id.id),
                ('date_from', '>=', self.from_date),
                ('date_to', '<=', self.to_date),
                ('state', 'in', ['done', 'paid', 'verify']),
            ])
           
            for slip in salary:
                for line in slip.line_ids:
                    if line.code == 'GROSS':
                        gross_pay += line.total
                    elif line.code == 'BASIC':
                        basic_pay += line.total
           # Sort the payslip lines by date to process them in chronological order
            sorted_payslip_lines = loan.payslip_line_ids.sorted(lambda l: l.date)
            for line in sorted_payslip_lines:
                date = line.date
                key = (date.month, date.year)
                if key not in payslip_lines:
                    payslip_lines[key] = {
                        'month_name': date.strftime('%B'),
                        'year': date.year,
                        'amount': 0,
                        'balance': remaining_balance,
                        'installments': remaining_installments
                    }
                payslip_lines[key]['amount'] += line.amount
                remaining_balance -= line.amount
                remaining_installments -= 1
                payslip_lines[key]['balance'] = remaining_balance
                payslip_lines[key]['installments'] = remaining_installments

            payslip_lines_list = list(payslip_lines.values())

            record_list.append({
                'from_date': self.from_date,
                'to_date': self.to_date,
                'loan_number': loan_number,
                'employee_name': employee_name,
                'date_birth': date_birth,
                'joining': joining,
                'appointment': appointment,
                'father_name': father_name,
                'department': department,
                'employee_type': employee_type,
                'designation': designation,
                'grade': grade,
                'gross_pay': gross_pay,
                'basic_pay': basic_pay,
                'return_mode': return_mode,
                'employee_code': employee_code,
                'date': request_date,
                'required_amount': required_amount,
                'installments': installments,
                'remarks': remarks,
                'service_duration': service_duration,
                'paid': paid,
                'deduction': deduction,
                'payslip_lines': payslip_lines_list,
                'emp_company': emp_company,
                'pf_emp': pf_emp,
                'pf_emper': pf_emper,
                'sum_pf': sum_pf,
                'balance': balance,
                'lum_sum': lum_sum,
                'write_off': write_off,
            })

        data = {
            'record_list': record_list,
            'from_month': from_month,
            'to_month': to_month,
            'from_year': from_year,
            'to_year': to_year,
            'company_name': self.env.company.name,
            'company_logo': self.env.company.logo,
        }
        return self.env.ref('pakgulf_employee_pf_loan_application.contribution_loan_details_report_action').report_action(self, data=data)
