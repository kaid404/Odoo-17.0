from odoo import api, models, _,fields,re
from num2words import num2words
from datetime import timedelta,datetime
import logging


_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    security_received_by = fields.Char(string="security_received_by")

    @api.model
    def security_amount_to_words(self, amount):
        """
        Convert a numeric amount into words.
        """
        return num2words(amount, lang='en').upper()


    # @api.constrains('payment_state')
    # def payment_create_user_function(self):
    #     for rec in self:
    #         if rec.payment_state != 'paid':
    #             if rec.payment_state == 'in_payment':
    #                 rec.payment_create_user = self.env.user.id
    #                 rec.payment_create_date = fields.Datetime.now()
    #             else:
    #                 rec.payment_create_user = False
    #                 rec.payment_create_date = False
    #
    #
    # def get_create_user(self):
    #     print('---------------------------------------------------------------------------------')
    #     if self.write_uid:
    #         return self.write_uid.name
    #     else:
    #         return False
    #
    #
    def get_write_date_Refund(self):
        print('---------------------------------------------------------------------------------')
        if self.write_date:
            write_date = self.write_date
            adjusted_time = write_date + timedelta(hours=5)
            adjusted_time = adjusted_time.date()
            adjusted_time = adjusted_time.strftime('%d-%b-%Y')
            # formatted_time = adjusted_time.strftime('%Y-%m-%d %I:%M:%S %p')
            # print('write--->', formatted_time)
            return adjusted_time
        else:
            return False

    def get_create_date_std(self):
        print('---------------------------------------------------------------------------------')
        if self.create_date:
            create_date = self.student_id.create_date
            adjusted_time = create_date + timedelta(hours=5)
            adjusted_time = adjusted_time.date()
            adjusted_time = adjusted_time.strftime('%d-%b-%Y')
            # formatted_time = adjusted_time.strftime('%Y-%m-%d %I:%M:%S %p')
            # print('create--->', formatted_time)
            return adjusted_time
        else:
            return False
    #
    # @api.model
    # def get_current_month_formatted(self):
    #     """
    #     Get the current month in Nov-2024 format.
    #     """
    #     print('-------current_date--------------------------------------------------------------------------')
    #     current_date = self.invoice_date
    #     print(current_date)
    #     return current_date.strftime('%b-%Y')
    #
    # @api.model
    # def extract_integers(self, value):
    #     """
    #     Extract integers from a string.
    #     """
    #     if value:
    #         # Use regex to extract integers
    #         integers = re.findall(r'\d+', value)
    #         # Join all found integers into a single string
    #         return " ".join(integers)
    #     return ""
