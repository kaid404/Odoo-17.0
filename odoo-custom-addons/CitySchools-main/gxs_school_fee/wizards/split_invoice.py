import pdb
import time
import datetime
import math

#from webob.datetime_utils import second

from odoo import api, fields, models, _, Command
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class GxsSplitInvoice(models.TransientModel):
    _name = 'gxs.split.invoice'
    _description = 'Split Invoice'

    @api.model
    def _get_invoice(self):
        if self.env.context.get('active_model', False) == 'account.move' and self.env.context.get('active_id', False):
            return self.env.context['active_id']


    invoice_id = fields.Many2one('account.move', string='Invoices', default=_get_invoice)
    amount = fields.Float('Total Amount',compute="compute_amount")
    installments = fields.Integer(string="No. of Installments",default=2,readonly=True)
    installment_amount = fields.Integer(string="Installment Amount")

    @api.depends('invoice_id')
    def compute_amount(self):
        for rec in self:
            if rec.invoice_id:
                if rec.invoice_id.state != 'draft':
                    raise UserError(_("Installments should be created only on draft status."))
                rec.amount = rec.invoice_id.amount_total
            else:
                rec.amount = 0.0



    @api.onchange('installments')
    def compute_installments_amount(self):
        for rec in self:
            if rec.installments < 2:
                raise UserError(_("Installments should not be less then 2"))
            elif rec.installments > 5:
                raise UserError(_("Installments should not be greater then 5"))
            else:
                rec.installment_amount = rec.amount / rec.installments



    def create_invoices(self):



        fine = 0
        for line1 in self.invoice_id.line_ids:
            if line1.product_id.name == 'Late Fee':
                fine = line1.price_total

        per_real = ((self.installment_amount - fine) / (self.amount-fine))
        second_per = 1 - per_real

        installment_no = self.invoice_id.installment_no
        child_move_ids = []
        per_number = 0
        for i in range(1,self.installments):
            if per_number == 0:
                per = second_per
            else:
                per = per_real
            per_number += 1
            installment_no += 1

            late_fine_lines = self.invoice_id.invoice_line_ids.filtered(lambda line: line.product_id.name != 'Late Fee')

            invoice_id = self.env['account.move'].create({
                'state': 'draft',
                'is_fee_invoice':True,
                'installment_no': installment_no,
                'partner_id': self.invoice_id.partner_id.id,
                'move_type': self.invoice_id.move_type,
                'journal_id': self.invoice_id.journal_id.id,
                'student_id': self.invoice_id.student_id.id,
                'invoice_date': self.invoice_id.invoice_date,
                'payment_reference': self.invoice_id.payment_reference,
                'invoice_line_ids': [(0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit * per,
                    'discount': line.discount,
                    'name': line.name,
                    'account_id': line.account_id.id,
                    # Add other necessary fields here
                }) for line in late_fine_lines],
            })

            for rec in self.invoice_id.line_ids:
                if rec.product_id.name != 'Late Fee':
                    # if self.installments >= 2 and rec.price_unit:
                    rec.price_unit = rec.price_unit * per_real

            child_move_ids.append(invoice_id.id)
        self.invoice_id.child_move_ids = child_move_ids
        self.invoice_id.action_post()
        for child in self.invoice_id.child_move_ids:
            child.action_post()
        return self.invoice_id.open_child_move_ids()
