from odoo import _, api, fields, models
from calendar import month_name
from dateutil.relativedelta import relativedelta
from datetime import datetime


class PakgulfEmpLoanApplication(models.TransientModel):
    _name = 'pak.emp.grant.loan.application'

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    employee_ids = fields.Many2many('hr.employee', string="Employee Name")

    def grant_loan_application_report(self):
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
            loan_type = ''
            payslip_lines = {}
            remaining_balance = loan.request_amount  # Initialize remaining balance with the loan amount
            remaining_installments = loan.duration_month  # Initialize remaining installments

            loan_number = loan.name
            employee_name = loan.employee_id.name
            date_birth = loan.employee_id.birthday
            employee_code = loan.employee_id.barcode
            emp_bank_name = loan.employee_id.bank_name
            emp_bank_account = loan.employee_id.bank_account
            type_loan = loan.payment
            if type_loan == 'partially':
                loan_type = loan.loan_type.name
            elif type_loan == 'fully':
                loan_type = 'Advance Loan'
            status = ''
            if loan.state == 'draft':
                status = 'Draft'
            elif loan.state == 'confirm':
                status = 'Confirmed'
            elif loan.state == 'approve1':
                status = 'Approve'
            elif loan.state == 'approve2':
                status = 'Approve'
            elif loan.state == 'paid':
                status = 'Paid'
            elif loan.state == 'done':
                status = 'Done'
            elif loan.state == 'refuse':
                status = 'Refuse'
            joining = loan.employee_id.contract_id.date_start
            emp_company = loan.employee_id.emp_company_id.name
            appointment = loan.employee_id.contract_id.date_start
            father_name = 'Father name'
            department = loan.employee_id.department_id.name
            designation = loan.employee_id.job_id.name
            if loan.employee_id.employee_type == 'employee':
                employee_type = 'Employee'
            elif loan.employee_id.employee_type == 'student':
                employee_type = 'Student'
            elif loan.employee_id.employee_type == 'trainee':
                employee_type = 'Trainee'
            elif loan.employee_id.employee_type == 'contractor':
                employee_type = 'Contractor'
            elif loan.employee_id.employee_type == 'freelance':
                employee_type = 'Freelancer'
            grade = loan.employee_id.x_studio_grade
            gross_pay = 0
            basic_pay = 0
            return_mode = ''
            if loan.payment == 'partially':
                return_mode = f'Monthly Installment, {loan.deduction_amount:.2f}'
            elif loan.payment == 'fully':
                return_mode = f'Full Payment, {loan.amount_to_pay:.2f}'

            deduction = loan.deduction_amount
            installments = loan.duration_month
            required_amount = loan.request_amount
            remarks = loan.reason
            request_date = loan.payment_start_date
            paid = loan.amount_paid
            balance = loan.amount_to_pay
             # Calculate the service duration
            contract_end_date = loan.employee_id.contract_id.date_end or datetime.today()
            service_duration_str = relativedelta(contract_end_date, joining)
            service_duration = f"{service_duration_str.years} years {service_duration_str.months} months {service_duration_str.days} days"
            pf_emp = 0
            pf_emper = 0
            sum_pf = 0
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
                    if line.code == 'PF':
                        pf_emp += line.total
                    elif line.code == 'PFEM':
                        pf_emper += line.total
                    elif line.code == 'GROSS':
                        gross_pay += line.total
                    elif line.code == 'BASIC':
                        basic_pay += line.total
                    
                    sum_pf = pf_emp + pf_emper
                   

        
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
                'from_date': self.from_date.strftime('%d-%m-%Y'),
                'to_date': self.to_date.strftime('%d-%m-%Y'),
                'loan_number': loan_number,
                'employee_name': employee_name,
                'date_birth': date_birth.strftime('%d-%m-%Y'),
                'joining': joining.strftime('%d-%m-%Y'),
                'appointment': appointment.strftime('%d-%m-%Y'),
                'father_name': father_name,
                'department': department,
                'employee_type': employee_type,
                'designation': designation,
                'grade': grade,
                'gross_pay': "{:,}".format(gross_pay),
                'basic_pay': "{:,}".format(basic_pay),
                'return_mode': "{:,}".format(return_mode),
                'employee_code': employee_code,
                'date': request_date.strftime('%d-%m-%Y'),
                'required_amount':  "{:,}".format(required_amount),
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
                'bank': emp_bank_name if emp_bank_name else 'N/A',
                'account#': emp_bank_account,
                'loan_type': loan_type if loan_type else 'N/A',
                'status': status,
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
        return self.env.ref('pakgulf_employee_pf_loan_application.emp_grant_loan_app_report_action').report_action(self, data=data)
