from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import date,timedelta

class StudentFee(models.Model):
    _inherit = 'op.student'

    class_id = fields.Many2one('op.academic.term', string='Academic Year', store=True, copy=True,tracking=True)
    year_id = fields.Many2one('op.academic.year', string='Academic Class', store=True, copy=True,tracking=True)
    section_id = fields.Many2one('class.section', string='Section',domain="[('class_id', '=',year_id)]",tracking=True)
    father_name = fields.Char(string="Father Name")

    id_old_student = fields.Boolean(string="Old Student")
    amount_fee = fields.Float(string='Fee Amount')
    def action_create_fee(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generate Monthly Invoices',
            'view_mode': 'form',
            'res_model': 'generate.monthly.invoices.wizard',

            'target': 'new',
        }




class AccountMove(models.Model):
    _inherit = 'account.move'
    super_invoice = fields.Many2one('account.move',string="Super Invoice" ,readonly=True)
    student_id = fields.Many2one('op.student',string="Student")
    is_fee_invoice = fields.Boolean(string='Is Fee invoice')
    invoice_payment_state = fields.Selection([('not_paid', 'Draft'),
                                                            ('open', 'Verify'),
                                                            ('unpaid', 'Issue To Student'),
                                                            ('paid', 'Paid'),
                                                            ('cancel', 'Cancelled')], default='not_paid', tracking=True,
                                             string='Payment Status')
    
    
    def action_mark_self(self):
        due_invoices = self.env['account.move'].search([('id','=',self.id),('invoice_date_due','<',date.today()),('state','=','posted'),
                                                       ('payment_state','in',['not_paid']),('is_fee_invoice','=',True),('super_invoice','=',False)])
        for inv in due_invoices:
            fee_st = self.env['fee.structure'].search([
                ('classes', '=', inv.student_id.year_id.id),
                ('date_start', '<=', date.today()),
                ('date_end', '>=', date.today()),
                ('company_id','=',inv.company_id.id)
            ], limit=1)

            l_fee = fee_st.late_fee
            if inv.company_id.id ==2:
                l_fee = 200
    
            if inv.is_fee_invoice == True:
                if inv.invoice_date_due < date.today() and l_fee > 0:
                    arrears_product = self.env['product.product'].search(
                        [('name', '=', 'Late Fee'), ('is_school_fee', '=', True)])
                    inv.button_draft()
                    line_rec = self.env['account.move.line'].create({
                            'move_id': inv.id,
                            'product_id': arrears_product.id,
                            'quantity': 1,
                            'price_unit': l_fee,
                            'account_id': arrears_product.property_account_income_id.id or arrears_product.categ_id.property_account_income_categ_id.id,
                        })
                    inv.super_invoice = inv.id
                    inv.action_post()
    def action_mark_fine(self):
        due_invoices = self.env['account.move'].search([('invoice_date_due','<',date.today()),('state','=','posted'),
                                                       ('payment_state','in',['not_paid']),('is_fee_invoice','=',True),('super_invoice','=',False)],limit=200)
        for inv in due_invoices:
            fee_st = self.env['fee.structure'].search([
                ('classes', '=', inv.student_id.year_id.id),
                ('date_start', '<=', date.today()),
                ('date_end', '>=', date.today()),
                ('company_id','=',inv.company_id.id)
            ], limit=1)
    
            if inv.is_fee_invoice == True:
                if inv.invoice_date_due < date.today() and fee_st.late_fee > 0:
                    arrears_product = self.env['product.product'].search(
                        [('name', '=', 'Late Fee'), ('is_school_fee', '=', True)])
                    inv.button_draft()
                    line_rec = self.env['account.move.line'].create({
                            'move_id': inv.id,
                            'product_id': arrears_product.id,
                            'quantity': 1,
                            'price_unit': fee_st.late_fee,
                            'account_id': arrears_product.property_account_income_id.id or arrears_product.categ_id.property_account_income_categ_id.id,
                        })
                    inv.super_invoice = inv.id
                    inv.action_post()


      
    
    
    
    

# class AccountPaymentRegister(models.TransientModel):
#     _inherit = 'account.payment.register'

#     def action_create_payments(self):
#         print('ffffffffffffffffffffffffffffffff')
#         inv = self.env['account.move'].search([('id','=',self.env.context.get('active_id'))])
#         if not inv and self.env.user.id == 4:
#             inv = self.env['account.move.history'].search([], order="id DESC", limit=1).xml_class_id

#         print(self.env.user)


#         print(inv)
#         # fee_st = self.env['fee.structure'].search([('classes', '=', inv.student_id.year_id.id)])

#         fee_st = self.env['fee.structure'].search([
#                 ('classes', '=', inv.student_id.year_id.id),
#                 ('date_start', '<=', date.today()),
#                 ('date_end', '>=', date.today())
#             ], limit=1)

#         if inv.is_fee_invoice == True:
#             if inv.invoice_date_due < date.today() and fee_st.late_fee > 0:
#                 invoice_lines = []
#                 arrears_product = self.env['product.product'].search([('name', '=', 'Late Fee'),('is_school_fee', '=',True)])
#                 if  0== 0 and inv.payment_state != 'partial':
#                     invoice_lines.append((0,0,{
#                         'product_id': arrears_product.id,
#                         'quantity': 1,
#                         'price_unit': fee_st.late_fee,
#                         'account_id': arrears_product.property_account_income_id.id or arrears_product.categ_id.property_account_income_categ_id.id,
#                     }))

#                     invoice_vals = {
#                         'super_invoice':inv.id,
#                         'partner_id': inv.partner_id.id,
#                         'move_type': 'out_invoice',
#                         'journal_id': self.env['account.journal'].search([('company_id', '=', inv.company_id.id), ('type',
#                                                                           'in',
#                                                                           [
#                                                                               'sale'])],
#                             limit=1).id,
#                         'invoice_date': date.today() + timedelta(days=15),
#                         'is_fee_invoice': True,
#                         'invoice_line_ids': invoice_lines,
#                     }
#                     print(invoice_vals)
#                     mo_id = self.env['account.move'].sudo().create(invoice_vals)
#                     mo_id.action_post()
#                     print(mo_id,'[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]')
#         res = super(AccountPaymentRegister, self).action_create_payments()
#         return res
