import logging
import calendar
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class OpusEmployeesPayrollReport(models.TransientModel):
    _name = 'opus.employees.payroll.report'
    _description = "Opus Employees Payroll Report"

    employee_id = fields.Many2many('hr.employee', string="Employee")
    payslip_run_id = fields.Many2one('hr.payslip.run', string="Batch")
    specific_date = fields.Date(string="Date")

    def get_report_data(self):
        domain = []
        days_in_month = 0
        remaining_amount_dict = {}
        if self.payslip_run_id:
            domain.append(('payslip_run_id', '=', self.payslip_run_id.id))
            start_date = self.payslip_run_id.date_start
            end_date = self.payslip_run_id.date_end

            # Calculate the number of days in the month
            days_in_month = (end_date - start_date).days + 1
        elif self.employee_id:
            if not self.specific_date:
                raise ValidationError("Please enter a specific date when an employee is selected.")

            domain.append(('employee_id', 'in', self.employee_id.ids))
            specific_date = self.specific_date
            first_day_of_month = specific_date.replace(day=1)
            last_day_of_month = specific_date.replace(
                day=calendar.monthrange(specific_date.year, specific_date.month)[1])
            if self.specific_date:
                domain.append(('date_from', '>=', first_day_of_month))
                domain.append(('date_from', '<=', last_day_of_month))
            if days_in_month == 0:
                days_in_month = (last_day_of_month - first_day_of_month).days + 1
                # for employee in self.employee_id:

            domain.append(('state', 'in', ['verify', 'done', 'paid']))

        payslips = self.env['hr.payslip'].search(domain)
        return payslips, days_in_month,

    # to_date = fields.Date('To Date', required=True)
    # company_id = fields.Many2many('employee.company.data', string="Company Name")

    # def print_com_wise_salary_report(self):
    #     record_list = []
    #     company_list = []
    #     company_list_abx = []
    #
    #     if not self.company_id:
    #         companies = self.env['employee.company.data'].search([])
    #     else:
    #         companies = self.company_id
    #
    #     for comp in companies:
    #         record_list = []
    #         employees = self.env['hr.employee'].search([('emp_company_id', '=', comp.id)])
    #         for rec in employees:
    #             st_gross = 0.0
    #             total_basic_salary = 0.0
    #             total_arees = 0.0
    #             total_mobile = 0.0
    #             total_food = 0.0
    #             total_late = 0.0
    #             total_absent = 0.0
    #             total_convance = 0.0
    #             total_gross = 0.0
    #             total_csmo = 0.0
    #             total_vehicle = 0.0
    #             total_Povid = 0.0
    #             total_eobi = 0.0
    #             total_pf_ded = 0.0
    #             total_salary_adv = 0.0
    #             total_ded_vehicle = 0.0
    #             total_net_pay = 0.0
    #             total_incom_tax = 0.0
    #             salary = self.env['hr.payslip'].search([
    #                 ('employee_id', '=', rec.id),
    #                 ('date_from', '>=', self.from_date),
    #                 ('date_to', '<=', self.to_date)
    #             ])
    #
    #             for slip in salary:
    #                 for line in slip.line_ids:
    #                     if line.code == 'SG':
    #                         st_gross = st_gross + line.total
    #                     if line.code == 'BASIC':
    #                         total_basic_salary = total_basic_salary + line.total
    #                     if line.code == 'AR':
    #                         total_arees = total_arees + line.total
    #                     if line.code == 'MA':
    #                         total_mobile = total_mobile + line.total
    #                     if line.code == 'CAFA':
    #                         total_convance = total_convance + line.total
    #                     if line.code == 'FA':
    #                         total_food = total_food + line.total
    #                     if line.code == 'LD':
    #                         total_late = total_late + line.total
    #                     if line.code == 'AD':
    #                         total_absent = total_absent + line.total
    #                     # if line.code == 'GROSS':
    #                     #     total_gross = total_gross + line.total
    #                     if line.code == 'Tax':
    #                         total_incom_tax = total_incom_tax + line.total
    #                     if line.name == 'Comp Loan':
    #                         total_csmo = total_csmo + line.total
    #                     if line.name == 'Vehicle Loan':
    #                         total_vehicle = total_vehicle + line.total
    #                     if line.code == 'PL':
    #                         total_Povid = total_Povid + line.total
    #                     if line.code == 'EOBIER':
    #                         total_eobi = total_eobi + line.total
    #                     if line.code == 'PFEM':
    #                         total_pf_ded = total_pf_ded + line.total
    #                     if line.code == 'ADV/SAL':
    #                         total_salary_adv = total_salary_adv + line.total
    #                     if line.code == 'DEDVEH':
    #                         total_ded_vehicle = total_ded_vehicle + line.total
    #                     if line.code == 'NET':
    #                         total_net_pay = total_net_pay + line.total
    #                     total_gross = (
    #                                           total_basic_salary + total_arees + total_mobile + total_convance + total_food) - (
    #                                           total_late + total_absent)
    #             record_list.append({
    #                 'company_name': rec.emp_company_id.name,
    #                 'from_date': self.from_date,
    #                 'to_date': self.to_date,
    #                 'st_gross': st_gross,
    #                 'total_basic_salary': total_basic_salary,
    #                 'total_arees': total_arees,
    #                 'total_mobile': total_mobile,
    #                 'total_convance': total_convance,
    #                 'total_food': total_food,
    #                 'total_late': total_late,
    #                 'total_absent': total_absent,
    #                 'total_gross': total_gross,
    #                 'total_csmo': total_csmo,
    #                 'total_vehicle': total_vehicle,
    #                 'total_Povid': total_Povid,
    #                 'total_eobi': total_eobi,
    #                 'total_pf_ded': total_pf_ded,
    #                 'total_salary_adv': total_salary_adv,
    #                 'total_ded_vehicle': total_ded_vehicle,
    #                 'total_net_pay': total_net_pay,
    #                 'total_incom_tax': total_incom_tax,
    #                 'code': rec.barcode,
    #                 'name': rec.name,
    #                 'cnic': rec.identification_id,
    #                 'Designation': rec.job_id.name,
    #                 'emp_company': rec.emp_company_id.id,
    #             })
    #         if record_list:
    #             company_list.append({'record_list': record_list, 'name': comp.name})
    #
    #     data = {
    #         'company_name': self.env.user.company_id.name,
    #         'company_logo': self.env.user.company_id.logo,
    #         'from_date': self.from_date,
    #         'to_date': self.to_date,
    #         'company_list': company_list,
    #     }
    #     return self.env.ref('pakgulf_hr_policies_and_reports.group_com_wise_salary_summary_report').report_action(self,
    #                                                                                                               data=data)

    def print_payroll_xlsx(self):
        print("Pakistan Zindabad-----------------------------------")
        data = {'id': self.id, }
        return self.env.ref('opus_payroll_report.group_summ_wise_xlsx').report_action(self, data=data)

    def print_pdf(self):
        payslips, days_in_month = self.get_report_data()
        employee_data = []
        total_basic = total_gross = total_fixed = total_house = total_utility = total_overtime = total_arrear = total_loan = total_increment = total_reimbursement = total_pf_emp = total_eobi_emp = total_pf_empl = total_eobi_empl = total_staff_adv = total_other_ded = total_income_tax = total_salary_payable = grand_total_payable = 0

        number_of_days = 0
        total_salary_payable = 0
        for slip in payslips:
            basic = fixed = house = utility = overtime = arrear = pf_emp = eobi_emp = loan = increment = reimbursement = pf_empl = eobi_empl = staff_adv = other_ded = income_tax = total_payable = 0
            total_gross += slip.contract_id.wage
            number_of_days = 0
            for a in slip.worked_days_line_ids:
                if a.name == 'Attendance':
                    number_of_days = a.number_of_days
            salary_payable = (slip.contract_id.wage / slip.cal_days) * number_of_days
            total_salary_payable += salary_payable

            increment = sum(slip.contract_id.increment_detail_ids.mapped('amount'))
            total_increment += increment


            for line in slip.line_ids:
                if line.code == "BASIC":
                    basic += line.total
                    total_basic += basic
                if line.code == "FXA":
                    fixed += line.total
                    total_fixed += fixed
                if line.code == "HA":
                    house += line.total
                    total_house += house
                if line.code == "UA":
                    utility += line.total
                    total_utility += utility
                if line.code == "OT":
                    overtime += line.total
                    total_overtime += overtime
                if 'ADV/SAL' in line.name:
                    loan = loan + line.total
                    total_loan += loan
                # if line.code == 'INC':
                #     increment += line.total
                #     total_increment += increment
                if line.code == 'REIMBURSEMENT':
                    reimbursement += line.total
                    total_reimbursement += reimbursement
                if line.code == "AR":
                    arrear += line.total
                    total_arrear += arrear
                if line.code == "PF":
                    pf_emp += line.total
                    total_pf_emp += pf_emp
                if line.code == "EOBI":
                    eobi_emp += line.total
                    total_eobi_emp += eobi_emp
                if line.code == "PFEM":
                    pf_empl += line.total
                    total_pf_empl += pf_empl
                if line.code == "EOBIE":
                    eobi_empl += line.total
                    total_eobi_empl += eobi_empl
                if 'ADV/SAL' in line.name:
                    staff_adv = staff_adv + line.total
                    total_staff_adv += staff_adv
                if line.code == "DEDUCTION":
                    other_ded += line.total
                    total_other_ded += other_ded
                if line.code == "IT":
                    income_tax += line.total
                    total_income_tax += income_tax
                if line.code == "NET":
                    total_payable += line.total
                    grand_total_payable += total_payable

            employee_data.append({
                'name': slip.employee_id.name,
                'code': slip.employee_id.barcode,
                'employment': dict(slip.employee_id._fields['employment'].selection).get(slip.employee_id.employment),
                'designation': slip.employee_id.contract_id.job_id.name,
                'location': slip.employee_id.work_location_id.name,
                'region': slip.employee_id.region_wise_detail,
                'doj': slip.employee_id.contract_id.date_start,
                'gross': slip.contract_id.wage,
                'days': days_in_month,
                'basic': round(basic),
                'fixed': round(fixed),
                'house': round(house),
                'utility': round(utility),
                'no_of_days': number_of_days,
                'salary_payable': round(salary_payable),
                'overtime': round(overtime),
                'loan': round(loan),
                'increment': round(increment),
                'reimbursement': round(reimbursement),
                'arrear': round(arrear),
                'pf_emp': round(pf_emp),
                'eobi_emp': round(eobi_emp),
                'pf_empl': round(pf_empl),
                'eobi_empl': round(eobi_empl),
                'staff_adv': round(staff_adv),
                'other_ded': round(other_ded),
                'income_tax': round(income_tax),
                'total_payable': round(total_payable),
                # 'payslip_lines': payslip_lines,
            })
        batch_name = f"For The Month Of {self.specific_date.strftime('%B %Y')}"
        data = {
            'employee_data': sorted(employee_data, reverse=False, key=lambda x: x['code']),
            'batch_name': batch_name,
            'total_gross': round(total_gross),
            'total_basic': total_basic,
            'total_salary_payable': total_salary_payable,
            'total_fixed': total_fixed,
            'total_house': total_house,
            'total_utility': total_utility,
            'total_overtime': total_overtime,
            'total_loan': total_loan,
            'total_increment': total_increment,
            'total_reimbursement': total_reimbursement,
            'total_arrear': total_arrear,
            'total_pf_emp': total_pf_emp,
            'total_eobi_emp': total_eobi_emp,
            'total_pf_empl': total_pf_empl,
            'total_eobi_empl': total_eobi_empl,
            'total_staff_adv': total_staff_adv,
            'total_other_ded': total_other_ded,
            'total_income_tax': total_income_tax,
            'grand_total_payable': grand_total_payable,

        }

        # data = {'docs': self.get_report_data()[0]}
        return self.env.ref('opus_payroll_report.payroll_report_action_pdf').report_action(self, data=data)
