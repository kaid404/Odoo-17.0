from odoo import api, models, _,fields
from num2words import num2words
from datetime import timedelta,datetime,date
import logging


_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"


    payment_create_user = fields.Many2one('res.users',string="Payment Create User")
    payment_create_date = fields.Datetime(string="Payment Create Date")
    student_id = fields.Many2one('op.student',string="Student")

    @api.model
    def amount_to_words(self, amount):
        """
        Convert a numeric amount into words.
        """
        return num2words(amount, lang='en').upper()

    def get_fine_amount_year_base_old2(self):
        if self.invoice_date.year == 2024 and self.company_id.id ==2:
            return 200
        else:
            fee_st = self.env['fee.structure'].search([
                ('classes', '=', self.student_id.year_id.id),
                ('date_start', '<=', self.invoice_date),
                ('date_end', '>=', self.invoice_date),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            return fee_st.late_fee


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


    def get_create_user_v(self):
        if self.payment_create_user:
            return self.payment_create_user.name
        else:
            return False


    def get_create_date_v(self):
        if self.payment_create_date:
            create_date = self.payment_create_date
            adjusted_time = create_date + timedelta(hours=5)
            formatted_time = adjusted_time.strftime('%Y-%m-%d %I:%M:%S %p')
            print('formatted_time--->', formatted_time)
            return formatted_time
        else:
            return False

    @api.model
    def get_current_month_formatted_old(self):
        """
        Get the current month in Nov-2024 format.
        """
        current_date = datetime.now()
        return current_date.strftime('%b-%Y')

    @api.model
    def get_late_fee(self):
        """Fetch late fee for a specific student based on the fee structure."""
        fee_structure = self.env['fee.structure'].search([
            ('classes', '=', self.student_id.year_id.id),
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        if self.super_invoice:
            return 0
        return fee_structure.late_fee if fee_structure else 0
