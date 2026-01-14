from odoo import models, fields, api, _
import logging
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime ,date
import odoo.addons.decimal_precision as dp
from dateutil import relativedelta
from calendar import monthrange
_logger = logging.getLogger(__name__)


class EmployeeAdvanceSalary(models.Model):
    _inherit = "hr.advance.salary"

    duration_month = fields.Integer('Payment Duration(month)', copy=False,tracking=True)

    def open_wizard_for_installments(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Change Installments",
            "res_model": "sync.adv.loan.update",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "context": {
                "salary_id": self.id,'amount_to_pay':self.amount_to_pay}
        }


class ReworksJobCard(models.TransientModel):
    _name = 'sync.adv.loan.update'
    _description = 'sync.adv.loan.update'

    salary_id = fields.Many2one('hr.advance.salary', string='Advance/Loan')
    amount = fields.Integer(string='Installment Amount')
    amount_to_pay = fields.Integer(string='Amount To Pay')
    installments = fields.Integer('Number of Installments')
    
    def by_amount(self):
        if self.amount == 0:
            raise ValidationError('Kindly select any amount.')
        if self.amount > self.salary_id.amount_to_pay:
            raise ValidationError('The entered amount is greater than the amount to pay.')
        
        payslip_ids = self.salary_id.payslip_line_ids.sorted(key=lambda a: a.date, reverse=True)
        st_date = self.salary_id.payment_start_date + timedelta(hours=5)
        st_date = st_date.date()
        
        date_payslip = max((p.payslip_id.date_to for p in payslip_ids), default=st_date)
        
        if not payslip_ids:
            # self.salary_id.advance_salary_line_ids.unlink()
            for dd in self.salary_id.advance_salary_line_ids:
                if dd.skip == False:
                    dd.unlink()
            date_payslip = st_date
        if payslip_ids:
            date_payslip = max(p.payslip_id.date_to for p in payslip_ids)
        
        paid_installments = len(self.salary_id.advance_salary_line_ids.filtered(lambda a: a.date <= date_payslip))
        future_lines = self.salary_id.advance_salary_line_ids.filtered(lambda x: x.date > date_payslip and x.skip == False)
        future_lines.unlink()
        if paid_installments == 0:
            # self.salary_id.advance_salary_line_ids.unlink()
            for dd in self.salary_id.advance_salary_line_ids:
                if dd.skip == False:
                    dd.unlink()
            date_payslip = st_date
        
        r = self.salary_id.advance_salary_line_ids
        
        skip_recs = self.env["hr.skip.installment"].search([
            ("employee_id", "=", self.salary_id.employee_id.id),
            ("advance_salary_id", "=", self.salary_id.id),('state','=','approve')
        ])
        skip_months_set = set((rec.date.year, rec.date.month) for rec in skip_recs)
        skip_dates = [rec.date.replace(day=1) for rec in skip_recs]
        
        payment_sum = 0.0
        i = 0
        current_date = st_date.replace(day=1)
        generated_dates = []
        
        latest_skip_date = max(skip_dates) if skip_dates else current_date
        
        while payment_sum < self.salary_id.amount_to_pay or current_date <= latest_skip_date:
            is_skip = (current_date.year, current_date.month) in skip_months_set
            _logger.info('---------------------------------------------')
            first_day = current_date.replace(day=1)

            # Last day of the month
            last_day = current_date.replace(day=monthrange(current_date.year, current_date.month)[1])
            line_old = self.env['hr.advance.salary.line'].search([('date','>=',first_day),('date','<=',last_day),('hr_advance_salary_id','=',self.salary_id.id)])
            if is_skip:
                pass
            elif line_old:  
                pass
                # amount =  
            else:
                remaining = self.salary_id.amount_to_pay - payment_sum
                if remaining <= self.amount:
                    amount = remaining
                else:
                    amount = self.amount
                payment_sum += amount
            
                self.env["hr.advance.salary.line"].create({
                    "hr_advance_salary_id": self.salary_id.id,
                    "date": current_date,
                    "amount": amount,
                    "employee_id": self.salary_id.employee_id.id,
                    "skip": is_skip,
                })
                
            generated_dates.append(current_date)
            current_date += relativedelta.relativedelta(months=1)
            i += 1
        
        self.salary_id.write({
            "duration_month": i,
            "deduction_amount": self.amount
        })
        
        # if self.amount == 0:
        #     raise ValidationError('kindly select any amount')
        # if self.amount > self.salary_id.amount_to_pay:
        #     raise ValidationError('The enter amount is grater then amount to pay')
        # number = 0
        # amount_to_pay = self.salary_id.amount_to_pay - self.amount
        # if self.amount > 0:
        #     self.installments = (self.salary_id.amount_to_pay / self.amount) + 1
        #
        # payslip_ids = self.salary_id.payslip_line_ids.sorted(key=lambda a: a.date, reverse=True)
        # date_payslip = date.today()
        # st_date = self.salary_id.payment_start_date + timedelta(hours=5)
        # st_date = st_date.date()
        # if not payslip_ids:
        #     self.salary_id.advance_salary_line_ids.unlink()
        #     date_payslip = st_date
        # if payslip_ids:
        #
        #     date_payslip = payslip_ids[0].payslip_id.date_to
        #     for ii in payslip_ids:
        #         if date_payslip < ii.payslip_id.date_to:
        #             date_payslip = ii.payslip_id.date_to
        # paid_installments = len(self.salary_id.advance_salary_line_ids.filtered(lambda a: a.date <= date_payslip))
        # # if self.installments <= paid_installments and paid_installments > 0:
        # #     raise ValidationError("Total number of installment must grater than paid installments.")
        # installment_ids = self.salary_id.advance_salary_line_ids.filtered(lambda x: x.date > date_payslip)
        # installment_ids.unlink()
        # if paid_installments == 0:
        #     self.salary_id.advance_salary_line_ids.unlink()
        #     date_payslip = st_date
        # r = self.salary_id.advance_salary_line_ids
        # x = 1
        # _logger.info(f'{r}/////////////////{st_date}')
        # max = self.installments
        #
        # amount_sum = 0
        # num = 0
        # for i in range(self.installments):
        #     num += 1
        #     print(i)
        #     if amount_sum < self.salary_id.amount_to_pay:
        #         payment_date = r[-1].date + relativedelta.relativedelta(
        #             months=x) if r else st_date + relativedelta.relativedelta(months=i)
        #         if num  == max:
        #             amount =  self.salary_id.amount_to_pay - amount_sum
        #         else:
        #             amount = self.amount
        #             amount_sum += self.amount
        #         self.env['hr.advance.salary.line'].create({
        #             'hr_advance_salary_id': self.salary_id.id,
        #             'date': payment_date,
        #             'amount': amount,
        #             'employee_id': self.salary_id.employee_id.id
        #         })
        #         x += 1
        #     else:
        #         self.installments = self.installments - 1
        # self.salary_id.write({'duration_month': self.installments + len(self.salary_id.payslip_line_ids),'deduction_amount':self.amount})

    def action(self):
        payslip_ids = self.salary_id.payslip_line_ids.sorted(key=lambda a: a.date, reverse=True)
        date_payslip = date.today()
        st_date = self.salary_id.payment_start_date + timedelta(hours=5)
        st_date = st_date.date()
        
        if not payslip_ids:
            # self.salary_id.advance_salary_line_ids.unlink()
            for dd in self.salary_id.advance_salary_line_ids:
                if dd.skip == False:
                    dd.unlink()
            date_payslip = st_date
        if payslip_ids:
            date_payslip = payslip_ids[0].payslip_id.date_to
            for ii in payslip_ids:
                if date_payslip < ii.payslip_id.date_to:
                    date_payslip = ii.payslip_id.date_to
        
        paid_installments = len(self.salary_id.advance_salary_line_ids.filtered(lambda a: a.date <= date_payslip))
        if self.installments <= paid_installments and paid_installments > 0:
            raise ValidationError("Total number of installments must be greater than paid installments.")
        installment_ids = self.salary_id.advance_salary_line_ids.filtered(lambda x: x.date > date_payslip and x.skip == False)
        installment_ids.unlink()
        
        if paid_installments == 0:
            # self.salary_id.advance_salary_line_ids.unlink()
            for dd in self.salary_id.advance_salary_line_ids:
                if dd.skip == False:
                    dd.unlink()
            date_payslip = st_date
        r = self.salary_id.advance_salary_line_ids
        skip_recs = self.env["hr.skip.installment"].search([
            ("employee_id", "=", self.salary_id.employee_id.id),
            ("advance_salary_id", "=", self.salary_id.id),('state','=','approve')
        ])
        skip_months = set(rec.date for rec in skip_recs)
        schedule_dates = []
        num_non_skip = 0
        if r:
            base_date = r[-1].date
        else:
            base_date = st_date

        if not payslip_ids:
            mo = 0
        else:
            mo = 1
        i = 0

        while num_non_skip < (self.installments - paid_installments):
            payment_date = base_date + relativedelta.relativedelta(months=i + mo)
            print(payment_date)
            schedule_dates.append(payment_date)
            if payment_date not in skip_months:
                num_non_skip += 1
            i += 1
        all_dates = set(schedule_dates) | skip_months
        sorted_dates = sorted(all_dates)

        total_real_payments = len([d for d in sorted_dates if d not in skip_months])
        if total_real_payments <= 0:
            raise ValidationError("No valid installment months found.")
        
        amount_per_payment = self.salary_id.amount_to_pay / total_real_payments

        for d in sorted_dates:
            is_skip = d in skip_months
            if is_skip:
                pass
            else:    
                self.env["hr.advance.salary.line"].create({
                    "hr_advance_salary_id": self.salary_id.id,
                    "date": d,
                    "amount": amount_per_payment,
                    "employee_id": self.salary_id.employee_id.id,
                    "skip": is_skip,
                })
        
        self.salary_id.write({"duration_month": self.installments})
        self.salary_id.write({
            "deduction_amount": amount_per_payment,
            "payment_end_date": max(sorted_dates)
        })
    
    # payslip_ids = self.salary_id.payslip_line_ids.sorted(key=lambda a:a.date, reverse=True)
        # date_payslip = date.today()
        # st_date = self.salary_id.payment_start_date + timedelta(hours=5)
        # st_date = st_date.date()
        # if not payslip_ids:
        #
        #     self.salary_id.advance_salary_line_ids.unlink()
        #     date_payslip = st_date
        # if payslip_ids:
        #     date_payslip = payslip_ids[0].payslip_id.date_to
        #     for ii in payslip_ids:
        #         if date_payslip < ii.payslip_id.date_to:
        #             date_payslip = ii.payslip_id.date_to
        # paid_installments = len(self.salary_id.advance_salary_line_ids.filtered(lambda a: a.date <= date_payslip))
        # if self.installments <= paid_installments and paid_installments > 0:
        #     raise ValidationError("Total number of installment must grater than paid installments.")
        # installment_ids = self.salary_id.advance_salary_line_ids.filtered(lambda x: x.date > date_payslip)
        # installment_ids.unlink()
        # if paid_installments == 0:
        #     self.salary_id.advance_salary_line_ids.unlink()
        #     date_payslip = st_date
        # r = self.salary_id.advance_salary_line_ids
        # x = 1
        # _logger.info(f'{r}/////////////////{st_date}')
        # # Collect dates of installments we will create
        # new_installment_dates = []
        # for i in range(self.installments - paid_installments):
        #     payment_date = r[-1].date + relativedelta.relativedelta(months=x) if r else st_date  + relativedelta.relativedelta(months=i)
        #     # self.env['hr.advance.salary.line'].create({
        #     #     'hr_advance_salary_id': self.salary_id.id,
        #     #     'date': payment_date,
        #     #     'amount': (self.salary_id.amount_to_pay / (self.installments - paid_installments)),
        #     #     'employee_id': self.salary_id.employee_id.id
        #     # })
        #     new_installment_dates.append(payment_date)
        #     x+=1
        #     # Query skip installment records for this employee and loan
        # skip_recs = self.env["hr.skip.installment"].search([
        #     ("employee_id", "=", self.salary_id.employee_id.id),
        #     ("advance_salary_id", "=", self.salary_id.id),
        # ])
        # skip_months = set()
        # for rec in skip_recs:
        #     skip_months.add(rec.date)
        #
        # for payment_date in sorted(new_installment_dates):
        #     is_skip = payment_date in skip_months
        #     self.env["hr.advance.salary.line"].create({
        #         "hr_advance_salary_id": self.salary_id.id,
        #         "date": payment_date,
        #         "amount": (
        #             0.0 if is_skip else (self.salary_id.amount_to_pay / (self.installments - paid_installments))
        #         ),
        #         "employee_id": self.salary_id.employee_id.id,
        #         "skip": is_skip
        #     })
        # self.salary_id.write({'duration_month':self.installments})
