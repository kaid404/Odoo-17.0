
from odoo import models, fields, api
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError



class AccountMove(models.TransientModel):
    _name = 'fee.discount.wizard'

    date = fields.Date(string='Date', default=lambda self: date.today(),required=True)
    student_id = fields.Many2one('op.student', string="Student",required=True)
    reason_discount = fields.Char(string="Reason for Discount",required=True)
    move_id = fields.Many2one('account.move',string="Fee Receipt",domain="[('student_id','=',student_id),('payment_state','=','not_paid')]",required=True)
    discount_amount = fields.Float('Amount')




    def action_done(self):
        if self.discount_amount > self.move_id.amount_total:
            raise ValidationError(_("Discount amount should not be grater than receipt amount."))

        fee_discount = self.create_fee_discount()
        fee_discount.action_confirm()

    def create_fee_discount(self):

        vals = {
            'date': self.date,
            'student_id': self.student_id.id,
            'reason_discount': self.reason_discount,
            'move_id': self.move_id.id,
            'discount_amount': self.discount_amount,
        }
        return self.env['fee.discount'].create(vals)
