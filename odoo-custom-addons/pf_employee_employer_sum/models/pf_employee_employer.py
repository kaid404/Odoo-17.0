from odoo import fields, models, api
import logging

logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Hr Employee'

    pf_employee_amount = fields.Float(string="Employee PF Amount", tracking=True)
    pf_employer_amount = fields.Float(string="Employer PF Amount", tracking=True)
    total_amount = fields.Float(string="Total PF Amount", store=True, tracking=True)

    total_pf_paid = fields.Float(string="Total PF Paid", store=True, tracking=True, readonly=True)
    pf_total_remaining = fields.Float(string="PF Remaining Amount", store=True, tracking=True, readonly=True)
    empl_opening = fields.Float(string="Employee PF Opening", tracking=True)
    empr_opening = fields.Float(string="Employer PF Opening", tracking=True)
    total_opening = fields.Float(string="Total PF Opening Amount", store=True, tracking=True)

    pf_employee_profit = fields.Float(string="Employee Profit PF Amount", readonly=True, tracking=True)
    pf_employer_profit = fields.Float(string="Employer Profit PF Amount", readonly=True, tracking=True)
    total_amount_profit = fields.Float(string="Total Profit PF Amount", readonly=True, store=True, tracking=True)
    pf_id = fields.Many2one('pf.employee.employer', string='PF Id')

    subtotal_pf = fields.Float(string="Total PF", compute='get_subtotal_pf')

    @api.depends('pf_employee_amount', 'pf_employer_amount', 'total_amount_profit', 'total_opening')
    def get_subtotal_pf(self):
        for rec in self:
            total = 00
            total += rec.pf_employee_amount + rec.pf_employer_amount + rec.total_amount_profit + rec.total_opening

            print(f'Starting Total: {total}')

            opening_loans = self.env['hr.advance.salary'].search([
                ('employee_id', '=', rec.id),
                ('payment', '=', 'partially'),
                ('loan_type.code', '=', 'PL'),
                ('state', 'in', ['paid','done','write_off']),
                ('opening_loan', '=', True)
            ])
            # opening_loan_amount = sum(opening_loans.mapped('amount_paid'))
            amount_to_pay = sum(opening_loans.mapped('amount_to_pay'))
            # print(f'opening loan paid amount: {opening_loan_amount}')

            # total += opening_loan_amount
            total += amount_to_pay
            print(f'total with opening loan paid amount: {total}')

            other_loans = self.env['hr.advance.salary'].search([
                ('employee_id', '=', rec.id),
                ('payment', '=', 'partially'),
                ('loan_type.code', '=', 'PL'),
                ('state', 'in', ['paid','done','write_off']),
                ('opening_loan', '=', False)
            ])

            requested_amount = sum(other_loans.mapped('request_amount'))
            # paid_amount = sum(other_loans.mapped('amount_paid'))
            amount_to_pay_2 = sum(other_loans.mapped('amount_to_pay'))

            print(f'without opening loan request amount: {requested_amount}')
            # print(f'without opening loan paid amount: {paid_amount}')

            total -= requested_amount
            print(f'total after difference of  without opening loan requested amount: {total}')
            # total += paid_amount
            total += amount_to_pay_2
            print(f'ALL TOTAL: {total}')

            rec.subtotal_pf = total

    def get_total_pf_paid(self):
        for rec in self:
            pf_records = self.env['pf.employee.employer'].search([('employee_id', '=', rec.id), ('state', '=', 'pay')])
            total_paid = sum(pf_records.mapped('current_paid_amount'))
            rec.total_pf_paid = total_paid

    def get_total_pf_remaining(self):
        for rec in self:
            pf_record = self.env['pf.employee.employer'].search([('employee_id', '=', rec.id), ('state', '=', 'pay')],
                                                                order='id desc', limit=1)
            rec.pf_total_remaining = pf_record.remaining_amount

    # def sum_pf_employee_employer(self):
    #     for record in self:
    #         employee_pf = self.env['hr.payslip'].search(
    #             [('employee_id', '=', record.id), ('state', 'in', ['verify', 'done', 'paid'])])
    #         paid_amounts = sum(self.env['pf.employee.employer'].search([('employee_id','=',record.id),('state', '=', 'pay')]).mapped('pay_amount')) or 0.0
    #         employee_pf_sum = 0
    #         employer_pf_sum = 0
    #         for line in employee_pf.line_ids:
    #             if line.code == 'PF':
    #                 employee_pf_sum = employee_pf_sum + line.total
    #             if line.code == 'PFEM':
    #                 employer_pf_sum = employer_pf_sum + line.total
    #         record.pf_employee_amount = employee_pf_sum
    #         record.pf_employer_amount = employer_pf_sum
    #         record.total_amount = record.pf_employee_amount + record.pf_employer_amount
    # record.paid_amount_pf = paid_amounts

    def sum_pf_employee_employer(self):
        for rec in self:
            logger.info("WorkingggggggggggggggggggggggG")
            profits = self.env['empl.empr.profit'].search([('name', '=', rec.id)])
            pf_employee_profit = sum(profits.mapped('employee_profit'))
            pf_employer_profit = sum(profits.mapped('employer_profit'))

            rec.pf_employee_profit = pf_employee_profit
            rec.pf_employer_profit = pf_employer_profit
            rec.total_amount_profit = pf_employee_profit + pf_employer_profit

            payslips = self.env['hr.payslip'].search([
                ('employee_id', '=', rec.id),
                ('state', 'in', ['done', 'verify', 'paid'])
            ])

            pf_employee_amount = sum(
                line.total for slip in payslips
                for line in slip.line_ids
                if line.code == 'PF' and line.slip_id.struct_id.name != 'Final Settlement'
            )

            pf_employer_amount = sum(
                line.total for slip in payslips
                for line in slip.line_ids
                if line.code == 'PFEM' and line.slip_id.struct_id.name != 'Final Settlement'
            )
            rec.pf_employee_amount = pf_employee_amount
            rec.pf_employer_amount = pf_employer_amount
            final_settlement_amount = sum(
                line.total for slip in payslips if 'Final Settlement' in slip.struct_id.name for line in slip.line_ids
                if line.name == 'PF Loan') or 0
            logger.info(f"Final Settlementttttttttttttttttttt {final_settlement_amount}")

            hr_advance_salary = self.env['hr.advance.salary'].search(
                [('employee_id', '=', rec.id), ('loan_type.name', '=', 'PF Loan'),
                 ('state', 'in', ['paid', 'done', 'write_off'])])
            logger.info(f"hr_advance_salaryyyyyyyyyyyyyyyyyyyyy {hr_advance_salary}")

            pf_loan_amount_paid = sum(self.env['hr.advance.salary'].search(
                [('employee_id', '=', rec.id), ('loan_type.name', '=', 'PF Loan'), ('opening_loan', '=', True),
                 ('state', 'in', ['paid', 'done', 'write_off'])]).mapped('amount_paid')) or 0.0
            opening_loans = hr_advance_salary.filtered(lambda r: r.opening_loan)
            not_opening_loans = hr_advance_salary.filtered(lambda r: r.opening_loan == False)

            total_request_amount = sum(opening_loans.mapped('request_amount'))
            total_paid_amount = sum(opening_loans.mapped('amount_paid'))
            not_total_request_amount = sum(not_opening_loans.mapped('request_amount'))
            not_total_paid_amount = sum(not_opening_loans.mapped('amount_paid'))

            if opening_loans:
                logger.info("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                if final_settlement_amount:
                    logger.info("A111111111111111111111111111111")
                    rec.total_amount = rec.empl_opening + rec.empr_opening + pf_employee_amount + pf_employer_amount + pf_loan_amount_paid + rec.total_amount_profit
                else:
                    logger.info("A222222222222222222222222222222")
                    rec.total_amount = rec.empl_opening + rec.empr_opening + pf_employee_amount + pf_employer_amount + total_paid_amount + rec.total_amount_profit
            else:
                logger.info("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
                if final_settlement_amount:
                    logger.info("B111111111111111111111111111")
                    rec.total_amount = rec.empl_opening + rec.empr_opening + pf_employee_amount + pf_employer_amount + pf_loan_amount_paid + rec.total_amount_profit
                else:
                    logger.info("B222222222222222222222222222")
                    rec.total_amount = rec.empl_opening + rec.empr_opening + pf_employee_amount + pf_employer_amount + not_total_paid_amount + rec.total_amount_profit

    def _compute_total_amount(self):
        for rec in self:
            rec.total_opening = rec.empl_opening + rec.empr_opening


class HrPayslip(models.Model):
    _inherit = 'hr.advance.salary'

    opening_loan = fields.Boolean(string='Opening Loan')

    # def compute_sheet(self):
    #     res = super(HrPayslip, self).compute_sheet()

    #     for payslip in self:
    #         employee = payslip.employee_id
    #         employee.sum_pf_employee_employer()
    #         employee._compute_total_amount()

    #     return res
