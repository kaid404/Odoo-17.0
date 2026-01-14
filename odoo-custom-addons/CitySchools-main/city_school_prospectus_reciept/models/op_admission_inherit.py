from odoo import api, models, _, fields, re
from num2words import num2words
from datetime import timedelta, datetime
import logging
import qrcode
import base64
from io import BytesIO

_logger = logging.getLogger(__name__)


class OpAdmission(models.Model):
    _inherit = "op.admission"

    @api.model
    def amount_to_words(self, amount):
        """
        Convert a numeric amount into words.
        """
        return num2words(amount, lang='en').upper()

    def get_create_user(self):
        print('---------------------------------------------------------------------------------')
        if self.create_uid:
            return self.create_uid.name
        else:
            return False

    def get_create_date(self):
        print('---------------------------------------------------------------------------------')
        if self.create_date:
            create_date = self.create_date
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
