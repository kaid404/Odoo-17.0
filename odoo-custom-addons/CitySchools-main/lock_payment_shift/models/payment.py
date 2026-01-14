from odoo import models,fields,api,_
from odoo.exceptions import UserError
from datetime import datetime,date,timedelta

class LockShiftDate(models.TransientModel):
    _name = 'lock.shift.date'
    _description = 'Lock Shift '

    closing_date_time = fields.Datetime('Closing Date')


    def close_shift(self):
        date = self.closing_date_time+timedelta(hours=5)
        print(date)
        return self.env['ir.config_parameter'].sudo().set_param("lock_payment_shift.city_shift_threshold", date)

# class RegisterPaymentMove(models.Model):
#     _inherit = 'account.move'
#
#     def action_register_payment(self):
#         # Check the configuration parameter value
#         shift_lock_enabled = self.env['ir.config_parameter'].sudo().get_param("lock_payment_shift.city_shift_threshold", "False")
#         if shift_lock_enabled == "False"  and self.move_type in ['out_invoice','out_refund']:
#             # If the parameter is True, proceed with the original functionality
#             raise UserError(_("Payments cannot be registered because payment shift has been closed.Please contact "
#                               "Administrator"))
#         else:
#             return super(RegisterPaymentMove, self).action_register_payment()

class RegPaymentWIzard(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.constrains('payment_date')
    def check_closing_date(self):
        # Fetch the parameter value as a string
        shift_lock_enabled = self.env['ir.config_parameter'].sudo().get_param("lock_payment_shift.city_shift_threshold")
        if shift_lock_enabled:
            try:
                # Convert the string to a datetime object
                shift_lock_date = datetime.strptime(shift_lock_enabled, "%Y-%m-%d %H:%M:%S")
                print(f"Parsed shift_lock_date: {shift_lock_date}")
            except ValueError:
                raise UserError(
                    _("Invalid date format for shift_lock_enabled parameter. Please check the configuration."))

            # Compare the date parts
            print(shift_lock_date.date())
            if self.payment_date <= shift_lock_date.date():
                raise UserError(_("Payments cannot be registered in back date as closing date has been restricted."))


