
from odoo import models, fields, api
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError



class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_fee_discount_wizard(self):
        # Return the action to open the wizard
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fee Discount Wizard',
            'res_model': 'fee.discount.wizard',  # Replace with the actual model of the wizard
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',  # Opens in a modal
            'context': {
                "default_student_id": self.student_id.id,
                "default_move_id": self.id,
                "default_date": date.today(),
            },
        }
