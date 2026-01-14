from odoo import api, models, _, fields, re
from num2words import num2words
from datetime import timedelta, datetime
import logging
import qrcode
import base64
from io import BytesIO

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_create_user = fields.Many2one('res.users', string="Payment Create User")
    payment_create_date = fields.Datetime(string="Payment Create Date")
    student_id = fields.Many2one('op.student', string="Student")

    @api.model
    def amount_to_words(self, amount):
        """
        Convert a numeric amount into words.
        """
        return num2words(amount, lang='en').upper()

    @api.constrains('payment_state')
    def payment_create_user_function(self):
        for rec in self:
            if rec.payment_state == 'paid':
                if 1==1:
                    rec.payment_create_user = self.env.user.id
                    rec.payment_create_date = fields.Datetime.now()
                else:
                    rec.payment_create_user = False
                    rec.payment_create_date = False

    def get_create_user(self):
        print('---------------------------------------------------------------------------------')
        if self.write_uid:
            payment = self.env['account.payment'].search([('ref', '=', self.name),('amount','=',self.amount_total)],limit=1)
            return payment.create_uid.name
        else:
            return False

    def get_create_date(self):
        print('---------------------------------------------------------------------------------')
        if self.write_date:
            payment = self.env['account.payment'].search([('ref', '=', self.name),('amount','=',self.amount_total)],limit=1)
            create_date = self.write_date
            create_date = self.invoice_date
            create_date = payment.create_date if payment.create_date else self.write_date 
            adjusted_time = create_date + timedelta(hours=5)
            formatted_time = adjusted_time.strftime('%Y-%m-%d %I:%M:%S %p')
            print('formatted_time--->', formatted_time)
            return formatted_time
        else:
            return False

    @api.model
    def get_current_month_formatted(self):
        """
        Get the current month in Nov-2024 format.
        """
        print('-------current_date--------------------------------------------------------------------------')
        current_date = self.invoice_date
        print(current_date)
        return current_date.strftime('%b-%Y')

    @api.model
    def extract_integers(self, value):
        """
        Extract integers from a string.
        """
        if value:
            # Use regex to extract integers
            integers = re.findall(r'\d+', value)
            # Join all found integers into a single string
            return " ".join(integers)
        return ""

    def get_installment_amount(self):
        print('self.amount_residual--------------------->', self.amount_residual)
        amt = sum(self.env['account.move'].search([('student_id','=',self.student_id.id),('payment_state','in',['not_paid']),('state','=','posted')]).mapped('amount_residual'))
        return amt
