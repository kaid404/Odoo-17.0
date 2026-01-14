import babel
from datetime import date, datetime, time

from dateutil.relativedelta import relativedelta
from datetime import date


from odoo import models, api, fields, tools, _
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.exceptions import ValidationError

from odoo import models, api, fields, _
import time
from dateutil.relativedelta import relativedelta


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def advance_salary_deduction(self):
        print('work111')
        # super(HrPayslip, self).action_payslip_done()
        super(HrPayslip, self).advance_salary_deduction()
        # super(HrPayslip, self).action_payslip_done()
    def compute_sheet(self):
        super(HrPayslip, self).compute_sheet()

        # count_late = self.env["late.check_in"].search(
        #     [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
        #      ('date', '<=', self.date_to), ('description', '=', ['Deduction from salary','Attendance Change Request'])
        #      ])
        # rs = 0
        # for amount in count_late:
        #     rs = rs + amount.amount
        #     print('ll,l', rs)
        # print(self.worked_days_line_ids[0].number_of_days)
        # net_selary = self.line_ids[-1].amount / self.worked_days_line_ids[0].number_of_days
        # rs = net_selary * rs
        # list_late = []
        # dic = {
        #     'name': ' Late deduction',
        #     'quantity': 1,
        #     'amount': -rs,
        #     'rate': 100,
        #     'salary_rule_id': 3,
        #     'code': 1,
        #     'category_id': 1,
        # }
        # list_late.append((0, 0, dic))
        # if rs > 0:
        #     self.write({'line_ids': list_late,
        #                 })
        #     self.line_ids[-1].total = self.line_ids[-1].total - rs
        #     self.line_ids[-1].amount = self.line_ids[-1].amount - rs
        #
        # return res

    # def compute_sheet(self):
    #     print('444444444444444444444444444411111111111')
    #     # need_approved = self.env['hr.leave'].search(
    #     #     [('employee_id.id', '=', self.employee_id.id),('state','!=','validate')])
    #     # if need_approved:
    #     #     raise ValidationError(("Some entries need approval first approve all Entries Pleas!"))
    #     # print('hi')
    #
    #     res = super(HrPayslip, self).compute_sheet()
    #     for payslip in self:
    #         payslip.advance_salary_deduction()
    #     payslips = self.filtered(lambda slip: slip.state in ['draft', 'verify'])
    #     # delete old payslip lines
    #     payslips.line_ids.unlink()
    #     for payslip in payslips:
    #         number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
    #         lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
    #         payslip.write({'line_ids': lines, 'number': number, 'state': 'verify', 'compute_date': fields.Date.today()})
    #
    #         count_late = self.env["late.check_in"].search(
    #             [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from),
    #
    #              ('date', '<=', self.date_to), ('description', '=', 'Deduction from salary')
    #              ])
    #         rs = 0
    #
    #         for amount in count_late:
    #             rs = rs + amount.amount
    #             print('ll,l', rs)
    #         print(self.worked_days_line_ids[0].number_of_days)
    #         net_selary = self.line_ids[-1].amount / self.worked_days_line_ids[0].number_of_days
    #         rs = net_selary * rs
    #         list_late = []
    #
    #         dic = {
    #             'name': ' Late deduction',
    #             'quantity': 1,
    #             'amount': -rs,
    #             'rate': 100,
    #             'salary_rule_id': 3,
    #             'code': 1,
    #             'category_id': 1,
    #         }
    #         list_late.append((0, 0, dic))
    #         if rs > 0:
    #
    #             self.write({'line_ids': list_late,
    #
    #                         })
    #
    #             self.line_ids[-1].total = self.line_ids[-1].total - rs
    #             self.line_ids[-1].amount = self.line_ids[-1].amount - rs
    #
    #         count_amount = self.env["hr.advance.salary"].search(
    #             [('payslip_loan_ids.employee_id', '=', self.employee_id.id), ('payslip_loan_ids.date', '>=', self.date_from),
    #
    #              ('payslip_loan_ids.date', '<=', self.date_to)
    #
    #              ])
    #         loan = 0
    #         full_loan = 0
    #         for i in count_amount.payslip_loan_ids:
    #             print(i.amount)
    #
    #             full_loan = full_loan + i.amount
    #             print(full_loan)
    #             if i.state == 'Draft':
    #
    #                 loan = loan + i.amount
    #                 # print(loan,i.amount)
    #                 i.write({'state': 'Conform'})
    #
    #                 if count_amount.amount_to_pay < loan:
    #                     raise ValidationError(("Total amount of loan deduction is greater then total payable amount"))
    #         if count_amount:
    #             count_amount.write({'amount_paid': count_amount.amount_paid + loan,
    #                                 'amount_to_pay': count_amount.amount_to_pay - loan})
    #         if full_loan > 0:
    #             list_late = []
    #             print(loan)
    #             print(full_loan)
    #             dic = {
    #                 'name': 'Loan Pay Off',
    #                 'quantity': 1,
    #                 'amount': -full_loan/2,
    #                 'rate': 100,
    #                 'salary_rule_id': 3,
    #                 'code': 1,
    #                 'category_id': 1,
    #             }
    #             print(dic, 'Dic')
    #             list_late.append((0, 0, dic))
    #             self.write({'line_ids': list_late,
    #
    #                         })
    #             print(rs)
    #             self.line_ids[-1].total = self.line_ids[-1].total - full_loan
    #             self.line_ids[-1].amount = self.line_ids[-1].amount - full_loan
    #             print(list_late)
    #             print(self.line_ids)
    #
    #             list_late = []
    #             dic = {
    #                 'employee_id': self.employee_id.id,
    #                 'payslip_id': self.id,
    #                 'amount': loan,
    #                 'date': date.today(),
    #
    #             }
    #             list_late.append((0, 0, dic))
    #             if loan > 0:
    #                 if count_amount.amount_to_pay != 0:
    #                     count_amount.write({'payslip_line_ids': list_late})
    #
    #
    #                 if count_amount.amount_to_pay == 0:
    #                     count_amount.write(
    #                         {'deduction_amount':0,'payment_end_date': count_amount.payslip_loan_ids.date, 'payslip_line_ids': list_late})
    #
    #     return res
