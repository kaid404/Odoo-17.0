from odoo import models, fields
import logging
from num2words import num2words
import datetime
from datetime import datetime
from datetime import date

logger = logging.getLogger(__name__)


class EmployeePayslipReport(models.Model):
    _inherit = 'hr.payslip'

    def action_print_payslip(self):
        contract = self.contract_id

        allowances_list = []
        deductions_list = []
        loans_list = []
        advances_list = []
        net_salary = 0.0
        net_salary_words = ""
        basic = 0
        allowances = 0
        late_deduction = 0
        absent_deduction = 0
        tax = 0
        # Dynamically get all allowances from payslip lines

        # Optionally update standard values from contract
        # if contract:
        #     for allowance in allowances_list:
        #         if allowance['Allowance Name'] == 'Mobile Allowance':
        #             allowance['Standard'] = contract.x_studio_mobile_allowance
        #         elif allowance['Allowance Name'] == 'Food Allowance':
        #             allowance['Standard'] = contract.x_studio_food_allowance
        #         # elif allowance['Allowance Name'] == 'Basic':
        #         #     allowance['Standard'] = contract.wage
        #         elif allowance['Allowance Name'] == 'Conveyance Allowance / Fuel Allowance':
        #             allowance['Standard'] = contract.x_studio_conveyance_allowance_fuel_allowance
        #         elif allowance['Allowance Name'] == 'House Rent Allowance':
        #             allowance['Standard'] = contract.x_studio_house_rent
        for line in self.line_ids:
            if line.category_id and (
                    'Allowance' in line.category_id.name or 'Basic' in line.category_id.name) and line.total > 0:
                standard = 0.0
                if contract:
                    if line.code == 'MA':
                        standard = contract.x_studio_mobile_allowance
                    elif line.code == 'FA':
                        standard = contract.x_studio_food_allowance
                    elif line.code == 'CAFA':
                        standard = contract.x_studio_conveyance_allowance_fuel_allowance
                    elif line.code == 'HR':
                        standard = contract.x_studio_house_rent
                    elif line.code == 'BASIC':
                        standard = contract.wage

                allowances_list.append({
                    'Allowance Name': line.name,
                    'Standard': standard,
                    'Current Month': line.total,
                })
                # allowances_list.append({
                #     'Allowance Name': line.name,
                #     'Standard': 0.0,
                #     'Current Month': line.total,
                # })

        current_month_deduction = 0

        loan_balance_net = 0

        for line in self.line_ids:
            current_month_deduction_pf = 0
            current_month_deduction_comp = 0
            current_month_deduction_veh = 0
            if line.category_id.code.startswith('DED'):
                ded_standard = 0.0
                if contract:
                    if line.code == 'EOBIEE':
                        ded_standard = line.total
                    elif line.code == 'PF':
                        ded_standard = line.total
                    elif line.code == 'Tax':
                        ded_standard = line.total
                    # elif line.name == 'House Rent':
                    #     ded_standard = contract.x_studio_house_rent
                deductions_list.append({
                    'Deduction Name': line.name,
                    'Standard': ded_standard,
                    'Amount': line.total,
                })

            elif line.category_id.code == 'NET':
                net_salary = line.total
                net_salary_words = num2words(net_salary, lang='en').upper()

            if line.code == 'ADV/SAL':
                current_month_deduction += line.total
                advances_list.append({
                    'current_month_deduction': current_month_deduction,
                })


            if 'Basic' in line.category_id.name:
                basic += line.total
            if 'Allowance' in line.category_id.name:
                allowances += line.total
            if 'LD' in line.code:
                late_deduction += line.total
            if 'AB' in line.code:
                absent_deduction += line.total
            if 'Tax' in line.code:
                tax += line.total

            advance_salary_records = self.env['hr.advance.salary'].search([('employee_id', '=', self.employee_id.id), ('name', '=', line.name)])
            for advance in advance_salary_records:
                if line.salary_rule_id.name == 'PF Loan' and line.name == advance.name:
                    current_month_deduction_pf += line.total

                if line.salary_rule_id.name == 'Comp Loan' and line.name == advance.name:
                    current_month_deduction_comp += line.total

                if line.salary_rule_id.name == 'Vehicle Loan' and line.name == advance.name:
                    current_month_deduction_veh += line.total

                if advance.payment == 'partially':
                    loan_balance_net += advance.amount_to_pay

                    if advance.loan_type.name == 'PF Loan':
                        monthly_deduction = current_month_deduction_pf or 1  # avoid zero
                        loans_list.append({
                            'Title': f"PF Loan ({line.name})",
                            'Sanctioned Amount': advance.request_amount,
                            'current_month_deduction': current_month_deduction_pf,
                            'Installment': round(advance.amount_to_pay / monthly_deduction) if monthly_deduction else 0,
                            'Balance': advance.amount_to_pay
                        })

                    elif advance.loan_type.name == 'Comp Loan':
                        monthly_deduction = current_month_deduction_comp or 1
                        loans_list.append({
                            'Title': f"Comp Loan ({line.name})",
                            'Sanctioned Amount': advance.request_amount,
                            'current_month_deduction': current_month_deduction_comp,
                            'Installment': round(advance.amount_to_pay / monthly_deduction) if monthly_deduction else 0,
                            'Balance': advance.amount_to_pay
                        })

                    elif advance.loan_type.name == 'Vehicle Loan':
                        monthly_deduction = current_month_deduction_veh or 1
                        loans_list.append({
                            'Title': f"Vehicle Loan ({line.name})",
                            'Sanctioned Amount': advance.request_amount,
                            'current_month_deduction': current_month_deduction_veh,
                            'Installment': round(advance.amount_to_pay / monthly_deduction) if monthly_deduction else 0,
                            'Balance': advance.amount_to_pay
                        })
            # elif advance.loan_type.name == 'Vehicle Loan':
            #    loan_balance_net += advance.amount_to_pay
            #    vehicle_loan_list.append({
            #        'Title': ' Vehicle Loan',
            #        'Sanctioned Amount': advance.request_amount,
            #        'Installment': advance.duration_month,
            #        'Balance': advance.amount_to_pay
            #    })
        worked_days = 0
        for work in self.worked_days_line_ids:
            if work.work_entry_type_id.name == 'Attendance':
                worked_days += work.number_of_days

        tax_slab = self.env['slab.configure'].search(
            [('fiscal_year_start', '<=', self.date_from), ('fiscal_year_end', '>=', self.date_to)]
        )
        logger.info("Slab")
        logger.info(tax_slab)
        payslip_date = self.date_from.month
        current_month = date.today().month
        texable = 0
        fiscal_month = 0
        z = 0
        payable = 0
        paid_tax = 0
        remaining = 0
        if tax_slab:
            if payslip_date >= 7:
                payslip_date = payslip_date - 1
                x = 12 - payslip_date
                fiscal_month = x + 6
                logger.info(fiscal_month)
            elif payslip_date < 7:
                fiscal_month = 7 - payslip_date
                logger.info(fiscal_month)

            texable = (basic + allowances) * 12
            # texable = ((basic + allowances) - (late_deduction + absent_deduction)) * fiscal_month
            logger.info('taxableeeeeeeeeeeeeeeeeeeeeeeeeee')
            logger.info('taxableeeeeeeeeeeeeeeeeeeeeeeeeee')
            logger.info('taxableeeeeeeeeeeeeeeeeeeeeeeeeee')
            logger.info(texable)

            z = texable
            # z = tax * fiscal_month
            logger.info(tax)
            logger.info(fiscal_month)
            logger.info(z)
            logger.info(tax_slab.slab1_1)
            logger.info(tax_slab.slab1_2)
            if z >= tax_slab.slab1_1 and z <= tax_slab.slab1_2:
                payable = z - tax_slab.slab1_1
                payable = (payable * (tax_slab.tax_perc / 100))
                payable = payable + tax_slab.tax_rate
                logger.info("AAAAAAAAAAAA")
                logger.info(payable)
            elif z >= tax_slab.slab2_1 and z <= tax_slab.slab2_2:
                payable = z - tax_slab.slab2_1
                payable = (payable * (tax_slab.tax_perc2 / 100))
                payable = payable + tax_slab.tax_rate2
                logger.info("BBBBBBBBBBBBBB")
                logger.info(payable)

            elif z >= tax_slab.slab3_1 and z <= tax_slab.slab3_2:
                payable = z - tax_slab.slab3_1
                payable = (payable * (tax_slab.tax_perc3 / 100))
                payable = payable + tax_slab.tax_rate3
            elif z >= tax_slab.slab4_1 and z <= tax_slab.slab4_2:
                payable = z - tax_slab.slab4_1
                payable = (payable * (tax_slab.tax_perc4 / 100))
                payable = payable + tax_slab.tax_rate4
            elif z >= tax_slab.slab5_1 and z <= tax_slab.slab5_2:
                payable = z - tax_slab.slab5_1
                payable = (payable * (tax_slab.tax_perc5 / 100))
                payable = payable + tax_slab.tax_rate5
            elif z >= tax_slab.slab6_1 and z <= tax_slab.slab6_2:
                payable = z - tax_slab.slab6_1
                payable = (payable * (tax_slab.tax_perc6 / 100))
                payable = payable + tax_slab.tax_rate6
            elif z >= tax_slab.slab7_1 and z <= tax_slab.slab7_2:
                payable = z - tax_slab.slab7_1
                payable = (payable * (tax_slab.tax_perc7 / 100))
                payable = payable + tax_slab.tax_rate7
            elif z >= tax_slab.slab8_1 and z <= tax_slab.slab8_2:
                payable = z - tax_slab.slab8_1
                payable = (payable * (tax_slab.tax_perc8 / 100))
                payable = payable + tax_slab.tax_rate8
            elif z >= tax_slab.slab9_1 and z <= tax_slab.slab9_2:
                payable = z - tax_slab.slab9_1
                payable = (payable * (tax_slab.tax_perc9 / 100))
                payable = payable + tax_slab.tax_rate9
            elif z >= tax_slab.slab10_1 and z <= tax_slab.slab10_2:
                payable = z - tax_slab.slab10_1
                payable = (payable * (tax_slab.tax_perc10 / 100))
                payable = payable + tax_slab.tax_rate10
            logger.info('payableeeeeeeeeeeeeeeeeeeeeeeeeee')
            logger.info('payableeeeeeeeeeeeeeeeeeeeeeeeeee')
            logger.info('payableeeeeeeeeeeeeeeeeeeeeeeeeee')
            logger.info('payableeeeeeeeeeeeeeeeeeeeeeeeeee')
            logger.info(payable)
            logger.info(tax_slab.slab2_1)
            logger.info(tax_slab.slab2_2)

            fiscal_year_start = tax_slab.fiscal_year_start if tax_slab else self.date_from
            previous_payslips = self.env['hr.payslip'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'paid'),
                # ('date_from', '>=', fiscal_year_start),
                # ('date_from', '<', self.date_from)
            ])
            logger.info('payslipsssssssssssssssssssssssssssssssssssssssss')
            logger.info('payslipsssssssssssssssssssssssssssssssssssssssss')
            logger.info(previous_payslips)
            paid_tax = sum(line.total for payslip in previous_payslips for line in
                           payslip.line_ids.filtered(lambda l: 'Tax' in l.code))
            logger.info(paid_tax)
            logger.info('dddddddddddddddddddddddddddddddddddddd')
            logger.info('dddddddddddddddddddddddddddddddddddddd')
            logger.info('dddddddddddddddddddddddddddddddddddddd')
            logger.info(paid_tax)
            remaining = payable - paid_tax
            logger.info('remaininggggggggggggggggggggggggggggg')
            logger.info('remaininggggggggggggggggggggggggggggg')
            logger.info(remaining)
            logger.info('paid_tax: %s', paid_tax)

        # logger.info('allowances_list: %s', allowances_list)
        # logger.info('deductions_list: %s', deductions_list)
        # logger.info('loans_list: %s', loans_list)
        # logger.info('advances_list: %s', advances_list)
        # logger.info('net_salary: %s', net_salary)
        # logger.info('net_salary_words: %s', net_salary_words)
        allowances_list = [allowance for allowance in allowances_list if allowance['Current Month'] != 0]
        deductions_list = [deduction for deduction in deductions_list if deduction['Amount'] != 0]
        data = {
            'docs_1': self.id,
            'allowances': allowances_list,
            'deductions': deductions_list,
            'net_salary': round(net_salary, 2),
            'net_salary_words': net_salary_words,
            'loans': loans_list,
            'advances': advances_list,
            'worked_days': worked_days,
            'loan_balance_net': loan_balance_net,
            'texable': texable,
            'payable': payable,
            'paid_tax': paid_tax,
            'remaining': remaining,
        }

        return self.env.ref('employee_payslip_report_pakgulf.employee_payslip_report_action').report_action(self,
                                                                                                            data=data)
