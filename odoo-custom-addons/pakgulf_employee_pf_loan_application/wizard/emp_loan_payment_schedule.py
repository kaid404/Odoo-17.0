from odoo import _, api, fields, models
from calendar import month_name
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import logging
import pytz

_logger = logging.getLogger(__name__)


class PakgulfEmpLoanApplication(models.TransientModel):
    _name = 'emp.loan.payment.schedule'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    employee_ids = fields.Many2many('hr.employee', string="Employee Name")
    loan_type = fields.Many2one('loan.type', string="Loan Type")
    loan_ids = fields.Many2many('hr.advance.salary', string="Loan")

    def loan_payment_schedule_report(self):
        record_list = []

        from_month = month_name[self.from_date.month]
        from_year = self.from_date.year
        to_month = month_name[self.to_date.month]
        to_year = self.to_date.year

        loan_domain = []
        if self.employee_ids:
            loan_domain.append(('employee_id', 'in', self.employee_ids.ids))
        if self.loan_type:
            loan_domain.append(('loan_type', '=', self.loan_type.id))
        if self.loan_ids:
            loan_domain.append(('id', 'in', self.loan_ids.ids))

        loan_reqs = self.env['hr.advance.salary'].search(loan_domain, order="employee_id ASC")
        loan_reqs = loan_reqs.filtered(lambda a: a.advance_salary_line_ids.filtered(lambda b: b.date >= self.from_date))
        employee_data = []
        for employee_id in loan_reqs.mapped('employee_id'):
            loan_data = []
            final_settlement = self.env['employee.final.settlement'].search([('name', '=', employee_id.id)], limit=1)
            _logger.info(final_settlement)
            _logger.info('final_settlement')
            for loan in loan_reqs.filtered(lambda a: a.employee_id.id == employee_id.id):
                loan_line_data = []
                if not loan.lum_sum and not loan.state == 'write_off' and not final_settlement:
                    _logger.info('-------------------- Enhanced Regular Loan Block --------------------')

                    journal_entry = self.env['account.move'].search(
                        [('acct_id2', '=', loan.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date)]
                    )

                    # Initialize running balances
                    opening_balance = loan.request_amount
                    principle_outstanding = loan.request_amount

                    for line in loan_reqs.mapped('advance_salary_line_ids').filtered(
                            lambda a: a.hr_advance_salary_id.id == loan.id):
                        lum_sum = 0
                        writeoff = 0
                        status = 'Unpaid'
                        principle_amount = 0
                        closing = opening_balance
                        total_amount = 0

                        # Check for both payslip deductions and journal entries
                        x = loan.payslip_line_ids.filtered(
                            lambda x: x.payslip_id.date_from.month == line.date.month
                                      and x.payslip_id.date_from.year == line.date.year
                        )

                        journal_match = journal_entry.filtered(
                            lambda j: j.date.month == line.date.month and j.date.year == line.date.year
                        )

                        if x and journal_match:
                            status = 'Lumsum+Paid'
                            debit_sum = sum(journal_match.mapped('line_ids').mapped('debit'))
                            principle_amount = x.amount
                            lum_sum = debit_sum

                            if not line.skip:
                                principle_amount = x.amount
                            elif line.skip:
                                status = 'Stopped'

                            closing = opening_balance - lum_sum
                            principle_outstanding = closing - principle_amount

                        elif x:
                            status = 'Paid'
                            principle_amount = x.amount
                            if not line.skip:
                                principle_amount = x.amount
                                closing = opening_balance - principle_amount
                                principle_outstanding = closing
                            elif line.skip:
                                status = 'Stopped'
                                closing = opening_balance
                                principle_outstanding = closing

                        elif journal_match:
                            # Only journal entry exists
                            status = 'Lum-Sum'
                            debit_sum = sum(journal_match.mapped('line_ids').mapped('debit'))
                            lum_sum = debit_sum
                            principle_amount = debit_sum
                            total_amount = debit_sum
                            closing = opening_balance - principle_amount
                            principle_outstanding = closing
                        else:
                            if line.skip:
                                status = 'Stopped'
                            if not line.skip:
                                principle_amount = line.amount

                        formatted_date = line.date.strftime('%B, %Y')

                        loan_line_data.append({
                            'date': formatted_date,
                            'opening': round(opening_balance),
                            'lum_sum': lum_sum if lum_sum else '',
                            'writeoff': writeoff if writeoff else '',
                            'closing': round(closing),
                            'principle_amount': round(principle_amount),
                            'total_amount': total_amount,
                            'outstanding_markup': 0,
                            'principle_outstanding': round(principle_outstanding),
                            'status': status,
                        })

                        # Update opening balance for next period
                        opening_balance = principle_outstanding

                        _logger.info(loan_line_data)
                elif loan.state == 'write_off' and not final_settlement:
                    _logger.info(
                        '-------------------------22222222-----------------------------------------------------')

                    journal_entry = self.env['account.move'].search(
                        [('acct_id2', '=', loan.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date)])

                    journal_dates = set(journal_entry.mapped('date'))
                    payslip_dates = set(loan.payslip_line_ids.mapped('payslip_id.date_from'))
                    all_dates = sorted(journal_dates.union(payslip_dates))

                    opening_balance = loan.request_amount
                    principle_outstanding = loan.request_amount
                    i = 0
                    length = len(all_dates)
                    for date_item in all_dates:
                        i += 1
                        status = 'Unpaid'
                        lum_sum = 0
                        writeoff = 0
                        principle_amount = 0
                        total_amount = 0
                        opening = 0
                        closing = opening_balance
                        principle_outstanding = 0

                        # Check if this month exists in payslip_line_ids
                        payslip_match = loan.payslip_line_ids.filtered(
                            lambda
                                x: x.payslip_id.date_from.month == date_item.month and x.payslip_id.date_from.year == date_item.year
                        )
                        journal_match = journal_entry.filtered(
                            lambda j: j.date.month == date_item.month and j.date.year == date_item.year
                        )

                        if payslip_match and journal_match:
                            status = 'Lumsum+Paid'
                            debit_sum = sum(journal_match.mapped('line_ids').mapped('debit'))
                            lum_sum = debit_sum

                            principle_amount = payslip_match.amount
                            closing = opening_balance - lum_sum
                            principle_outstanding = closing - principle_amount


                        elif payslip_match:
                            status = 'Paid'
                            principle_amount = payslip_match.amount
                            closing = opening_balance - principle_amount
                            principle_outstanding = closing

                        elif journal_match:
                            status = 'Lum-Sum'
                            debit_sum = sum(journal_match.mapped('line_ids').mapped('debit'))
                            lum_sum = debit_sum
                            principle_amount = debit_sum
                            total_amount = debit_sum
                            closing = opening_balance - principle_amount
                            principle_outstanding = closing

                        loan_line_data.append({
                            'date': date_item.strftime('%B, %Y'),
                            'opening': round(opening_balance),
                            'lum_sum': lum_sum,
                            'writeoff': writeoff if writeoff else '',
                            'closing': round(closing),
                            'principle_amount': round(principle_amount),
                            'total_amount': total_amount,
                            'outstanding_markup': 0,
                            'principle_outstanding': round(principle_outstanding),
                            'status': status,
                        })
                        opening_balance = principle_outstanding

                        _logger.info(loan_line_data)

                    if all_dates:
                        last_date = all_dates[-1]
                        matured_date = (last_date.replace(day=1) + relativedelta(months=1))
                        loan_line_data.append({
                            'date': matured_date.strftime('%B, %Y'),
                            'opening': round(opening_balance),
                            'lum_sum': 0,
                            'writeoff': round(loan.amount_to_pay),
                            'closing': 0,
                            'principle_amount': 0,
                            'total_amount': 0,
                            'outstanding_markup': 0,
                            'principle_outstanding': 0,
                            'status': 'Matured',
                        })
                elif final_settlement:
                    _logger.info('-------------------------33333333--------------------------------')

                    journal_entry = self.env['account.move'].search(
                        [('acct_id2', '=', loan.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date)])

                    journal_dates = set(journal_entry.mapped('date'))
                    payslip_dates = set(loan.payslip_line_ids.mapped('payslip_id.date_from'))
                    all_dates = sorted(journal_dates.union(payslip_dates))

                    opening_balance = loan.request_amount
                    principle_outstanding = loan.request_amount
                    i = 0
                    length = len(all_dates)
                    for date_item in all_dates:
                        i += 1
                        status = 'Unpaid'
                        lum_sum = 0
                        writeoff = 0
                        principle_amount = 0
                        total_amount = 0
                        opening = 0
                        closing = opening_balance
                        principle_outstanding = 0

                        # Check if this month exists in payslip_line_ids
                        payslip_match = loan.payslip_line_ids.filtered(
                            lambda
                                x: x.payslip_id.date_from.month == date_item.month and x.payslip_id.date_from.year == date_item.year
                        )
                        journal_match = journal_entry.filtered(
                            lambda j: j.date.month == date_item.month and j.date.year == date_item.year
                        )

                        if payslip_match and journal_match:
                            status = 'Lumsum+Paid'
                            debit_sum = sum(journal_match.mapped('line_ids').mapped('debit'))
                            lum_sum = debit_sum

                            principle_amount = payslip_match.amount
                            closing = opening_balance - lum_sum
                            principle_outstanding = closing - principle_amount


                        elif payslip_match:
                            status = 'Paid'
                            principle_amount = payslip_match.amount
                            closing = opening_balance - principle_amount
                            principle_outstanding = closing

                        elif journal_match:
                            status = 'Lum-Sum'
                            debit_sum = sum(journal_match.mapped('line_ids').mapped('debit'))
                            lum_sum = debit_sum
                            principle_amount = debit_sum
                            total_amount = debit_sum
                            closing = opening_balance - principle_amount
                            principle_outstanding = closing

                        loan_line_data.append({
                            'date': date_item.strftime('%B, %Y'),
                            'opening': round(opening_balance),
                            'lum_sum': lum_sum,
                            'writeoff': writeoff if writeoff else '',
                            'closing': round(closing),
                            'principle_amount': round(principle_amount),
                            'total_amount': total_amount,
                            'outstanding_markup': 0,
                            'principle_outstanding': round(principle_outstanding),
                            'status': status,
                        })
                        opening_balance = principle_outstanding

                        _logger.info(loan_line_data)

                    if all_dates:
                        last_date = all_dates[-1]
                        next_month = last_date.replace(day=1) + relativedelta(months=1)

                        final_date = final_settlement.resign_date
                        final_month = date(final_date.year, final_date.month, 1)

                        while next_month < final_month:
                            stopped_opening = opening_balance
                            stopped_closing = stopped_opening
                            loan_line_data.append({
                                'date': next_month.strftime('%B, %Y'),
                                'opening': round(stopped_opening),
                                'lum_sum': 0,
                                'writeoff': '',
                                'closing': round(stopped_closing),
                                'principle_amount': 0,
                                'total_amount': 0,
                                'outstanding_markup': 0,
                                'principle_outstanding': round(stopped_closing),
                                'status': 'Stopped',
                            })
                            next_month += relativedelta(months=1)

                        # Add final matured line
                        loan_line_data.append({
                            'date': final_month.strftime('%B, %Y'),
                            'opening': round(opening_balance),
                            'lum_sum': round(loan.amount_to_pay),
                            'writeoff': '',
                            'closing': 0,
                            'principle_amount': 0,
                            'total_amount': 0,
                            'outstanding_markup': 0,
                            'principle_outstanding': 0,
                            'status': 'Matured',
                        })
                    else:
                        request_month = fields.Date.to_date(loan.request_date)  # Convert safely
                        final_date = final_settlement.resign_date
                        final_month = date(final_date.year, final_date.month, 1)

                        next_month = request_month.replace(day=1)

                        while next_month < final_month:
                            loan_line_data.append({
                                'date': next_month.strftime('%B, %Y'),
                                'opening': round(loan.request_amount),
                                'lum_sum': 0,
                                'writeoff': '',
                                'closing': round(loan.request_amount),
                                'principle_amount': 0,
                                'total_amount': 0,
                                'outstanding_markup': loan.request_amount,
                                'principle_outstanding': round(loan.request_amount),
                                'status': 'Stopped',
                            })
                            next_month += relativedelta(months=1)

                        loan_line_data.append({
                            'date': final_month.strftime('%B, %Y'),
                            'opening': round(loan.request_amount),
                            'lum_sum': round(loan.amount_to_pay),
                            'writeoff': '',
                            'closing': 0,
                            'principle_amount': 0,
                            'total_amount': 0,
                            'outstanding_markup': 0,
                            'principle_outstanding': 0,
                            'status': 'Matured',
                        })



                    # if all_dates:
                    #     last_date = all_dates[-1]
                    #     matured_date = (last_date.replace(day=1) + relativedelta(months=1))
                    #     loan_line_data.append({
                    #         'date': matured_date.strftime('%B, %Y'),
                    #         'opening': round(opening_balance),
                    #         'lum_sum': round(loan.amount_to_pay),
                    #         'writeoff': 0,
                    #         'closing': 0,
                    #         'principle_amount': 0,
                    #         'total_amount': 0,
                    #         'outstanding_markup': 0,
                    #         'principle_outstanding': 0,
                    #         'status': 'Matured',
                    #     })
                    # if all_dates:
                    #     last_date = all_dates[-1]
                    #
                    #     stopped_date = (last_date.replace(day=1) + relativedelta(months=1))
                    #     stopped_opening = opening_balance
                    #     stopped_closing = stopped_opening
                    #     loan_line_data.append({
                    #         'date': stopped_date.strftime('%B, %Y'),
                    #         'opening': round(stopped_opening),
                    #         'lum_sum': 0,
                    #         'writeoff': '',
                    #         'closing': round(stopped_closing),
                    #         'principle_amount': 0,
                    #         'total_amount': 0,
                    #         'outstanding_markup': 0,
                    #         'principle_outstanding': round(stopped_closing),
                    #         'status': 'Stopped',
                    #     })
                    #
                    #     matured_date = stopped_date + relativedelta(months=1)
                    #     loan_line_data.append({
                    #         'date': matured_date.strftime('%B, %Y'),
                    #         'opening': round(stopped_closing),
                    #         'lum_sum': round(loan.amount_to_pay),
                    #         'writeoff': '',
                    #         'closing': 0,
                    #         'principle_amount': 0,
                    #         'total_amount': 0,
                    #         'outstanding_markup': 0,
                    #         'principle_outstanding': 0,
                    #         'status': 'Matured',
                    #     })


                elif loan.lum_sum:
                    _logger.info('-------------------------4444-----------------------------------------------------')
                    journal_entry = self.env['account.move'].search(
                        [('acct_id2', '=', loan.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date)])

                    journal_dates = set(journal_entry.mapped('date'))
                    payslip_dates = set(loan.payslip_line_ids.mapped('payslip_id.date_from'))
                    all_dates = sorted(journal_dates.union(payslip_dates))

                    i = 0
                    length = len(all_dates)
                    opening_balance = loan.request_amount
                    principle_outstanding = loan.request_amount

                    for date_item in all_dates:
                        i += 1
                        status = 'Unpaid'
                        lum_sum = 0
                        writeoff = 0

                        principle_amount = 0
                        total_amount = 0
                        opening = 0
                        closing = opening_balance
                        principle_outstanding = 0

                        payslip_match = loan.payslip_line_ids.filtered(
                            lambda
                                x: x.payslip_id.date_from.month == date_item.month and x.payslip_id.date_from.year == date_item.year
                        )
                        journal_match = journal_entry.filtered(
                            lambda j: j.date.month == date_item.month and j.date.year == date_item.year
                        )
                        if payslip_match and journal_match:
                            status = 'Lumsum+Paid'
                            debit_sum = sum(journal_match.mapped('line_ids').mapped('debit'))
                            lum_sum = debit_sum

                            principle_amount = payslip_match.amount
                            closing = opening_balance - lum_sum
                            principle_outstanding = closing - principle_amount


                        elif payslip_match:
                            status = 'Paid'
                            principle_amount = payslip_match.amount
                            closing = opening_balance - principle_amount
                            principle_outstanding = closing

                        elif journal_match:
                            status = 'Lum-Sum'
                            debit_sum = sum(journal_match.mapped('line_ids').mapped('debit'))
                            lum_sum = debit_sum
                            principle_amount = debit_sum
                            total_amount = debit_sum
                            closing = opening_balance - principle_amount
                            principle_outstanding = closing

                        # if payslip_match:
                        #     status = 'Paid'
                        #     # Match advance salary line for that month
                        #     line_match = loan.advance_salary_line_ids.filtered(
                        #         lambda
                        #             l: l.date.month == date_item.month and l.date.year == date_item.year and not l.skip
                        #     )
                        #     principle_amount = sum(line_match.mapped('amount'))
                        #     total_amount = principle_amount
                        #     opening = sum(loan.advance_salary_line_ids.filtered(
                        #         lambda a: a.date >= date_item and not a.skip
                        #     ).mapped('amount'))
                        #     closing = opening
                        #     p_out = closing - total_amount
                        #
                        # # Else → Not in payslip, check in journal
                        # else:
                        #     if journal_match:
                        #         status = 'Lum-Sum'
                        #         # Sum debit from journal entry lines
                        #         debit_sum = sum(journal_match.mapped('line_ids').mapped('debit'))
                        #         opening = debit_sum
                        #         lum_sum = debit_sum
                        #         principle_amount = debit_sum
                        #         total_amount = debit_sum
                        #         closing = debit_sum
                        #         p_out = closing - principle_amount

                        if i == length:
                            status = 'Matured'
                            closing = 0
                            p_out = 0
                            principle_amount = 0
                            total_amount = 0
                            lum_sum = opening

                        loan_line_data.append({
                            'date': date_item.strftime('%B, %Y'),
                            'opening': round(opening_balance),
                            'lum_sum': lum_sum,
                            'writeoff': writeoff if writeoff else '',
                            'closing': round(closing),
                            'principle_amount': round(principle_amount),
                            'total_amount': total_amount,
                            'outstanding_markup': 0,
                            'principle_outstanding': round(principle_outstanding),
                            'status': status,
                        })
                        opening_balance = principle_outstanding
                        _logger.info(loan_line_data)


                else:
                    _logger.info('-------------------------55555-----------------------------------------------------')
                    i = 0
                    length = len(loan_reqs.mapped('advance_salary_line_ids').filtered(
                        lambda a: a.hr_advance_salary_id.id == loan.id and a.date <= loan.payment_end_date.date()))
                    for line in loan_reqs.mapped('advance_salary_line_ids').filtered(
                            lambda a: a.hr_advance_salary_id.id == loan.id and a.date <= loan.payment_end_date.date()):
                        i += 1
                        status = 'Unpaid'
                        lum_sum = 0
                        writeoff = 0
                        x = loan.payslip_line_ids.filtered(lambda
                                                               x: x.payslip_id.date_from.month == line.date.month and x.payslip_id.date_from.year == line.date.year)
                        if x:
                            status = 'Paid'
                        elif line.skip == True:
                            status = 'Stopped'
                        opening = sum(loan_reqs.mapped('advance_salary_line_ids').filtered(lambda
                                                                                               a: a.hr_advance_salary_id.id == loan.id and a.date >= line.date and a.skip == False).mapped(
                            'amount'))
                        _logger.info(opening)
                        # closing = opening - lum_sum
                        if i == length:
                            opening = loan.deduction_amount
                            lum_sum = loan.deduction_amount
                            principle_amount = 0
                            closing = 0
                            status = 'Matured'
                            total_amount = 0
                            p_out = 0
                        else:
                            closing = opening
                        _logger.info(closing)
                        total_amount = line.amount
                        if status != 'Stopped' and i != length:
                            principle_amount = line.amount
                            total_amount = line.amount
                            formatted_date = line.date.strftime('%B, %Y')
                        else:
                            principle_amount = 0
                            total_amount = 0
                            formatted_date = line.date.strftime('%B, %Y')
                        if i == length:
                            p_out = 0
                        else:
                            p_out = closing - total_amount
                        if loan.state == 'write_off' and loan.write_date.date() <= line.date:
                            principle_amount = 0
                            p_out = 0
                            total_amount = 0
                            writeoff = line.amount
                            status = 'Write Off'
                        # if lum_sum:
                        #     principle_amount = 0
                        #     p_out = 0
                        #     total_amount = 0
                        #     lum_sum = line.amount
                        #     status = 'Lum-Sum'
                        loan_line_data.append({
                            'date': formatted_date,
                            'opening': round(opening),
                            'lum_sum': lum_sum,
                            'writeoff': writeoff if writeoff else '',
                            'closing': round(closing),
                            'principle_amount': round(principle_amount),
                            'total_amount': total_amount,
                            'outstanding_markup': 0,
                            'principle_outstanding': round(p_out),
                            'status': status,
                        })
                        _logger.info(loan_line_data)
                loan_data.append({
                    'loan_no': loan.name,
                    'loan_type': loan.loan_type.name,
                    'deduction': loan.deduction_amount,
                    'loan_sectioned': loan.request_amount,
                    'loan_paid': loan.amount_paid if not final_settlement else loan.request_amount,
                    'date': loan.payment_start_date.astimezone(pytz.timezone('Asia/Karachi')).strftime('%d-%m-%Y'),
                    'starts_from': loan.duration_month,
                    'installments': loan.duration_month,
                    'loan_line_data': loan_line_data,
                })
            joining = employee_id.contract_id.date_start
            contract_end_date = employee_id.contract_id.date_end or datetime.today()
            service_duration_str = relativedelta(contract_end_date, joining)
            service_duration = f"{service_duration_str.years} years {service_duration_str.months} months {service_duration_str.days} days"

            employee_data.append({
                'employee_id': employee_id.id,
                'badge': employee_id.barcode,
                'name': employee_id.name,
                'date_birth': employee_id.birthday.strftime('%d-%m-%Y') if employee_id.birthday else '',
                'employee_code': employee_id.barcode,
                'joining': joining.strftime('%d-%m-%Y') if employee_id.contract_id.date_start else '',
                'service_duration': service_duration,
                'loan_data': loan_data,
            })

        data = {
            'employee_data': employee_data,
            'from_month': from_month,
            'to_month': to_month,
            'from_year': from_year,
            'to_year': to_year,
            'company_name': self.env.company.name,
            'company_logo': self.env.company.logo,
        }
        return self.env.ref(
            'pakgulf_employee_pf_loan_application.emp_loan_payment_schedule_report_action').report_action(self,
                                                                                                          data=data)
