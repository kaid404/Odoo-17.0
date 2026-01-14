
from odoo import models, fields, api
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError



class FeeReportWizard(models.Model):
    _name = 'fee.discount'
    _description = 'Fee Discount'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=False, readonly=True, default='New', store=True)
    date = fields.Date(string='Date', default=lambda self: date.today(),required=True)
    student_id = fields.Many2one('op.student', string="Student",required=True)
    state = fields.Selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],string="Status",default="draft")
    reason_discount = fields.Char(string="Reason for Discount",required=True)
    move_id = fields.Many2one('account.move',string="Fee Receipt",domain="[('student_id','=',student_id),('payment_state','=','not_paid')]",required=True)
    discount_amount = fields.Float('Amount')



    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.fee.discount') or 'New'
        result = super(FeeReportWizard, self).create(vals)
        return result


    def action_confirm(self):
        if self.discount_amount > self.move_id.amount_total:
            raise ValidationError(_("Discount amount should not be grater than receipt amount."))

        self.update_move_id()
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def update_move_id(self):

        vals = {
            'account_id': 142,
            'name': f"(Discount) {self.reason_discount}",
            'quantity': 1,
            'price_unit': -self.discount_amount,
            'move_id': self.move_id.id
        }
        self.move_id.button_draft()
        self.env['account.move.line'].create(vals)
        self.move_id.action_post()
