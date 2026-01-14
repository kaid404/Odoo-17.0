from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime,timedelta,date
import calendar
import logging
_logger = logging.getLogger(__name__)
class FeeStructure(models.Model):
    _name = 'fee.structure'
    _description = 'Fee Structure'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']
    _rec_name = "classes"

    name = fields.Char(string='Name', required=False, readonly=True, default='New', store=True)
    classes = fields.Many2one('op.academic.year', string='Class', store=True, copy=True, tracking=True)
    date_start = fields.Date('Date Start', store=True, copy=False, tracking=True)
    date_end = fields.Date('Date End', store=True, copy=False, tracking=True)
    fee_details = fields.One2many('fee.details', 'structure_id', string='Fee Details', copy=True)

    late_fee = fields.Integer(string='Late Fee', tracking=True)
    admission_fee = fields.Integer(string='Admission Fee', tracking=True)
    annual_charges = fields.Integer(string='Annual Charges', tracking=True)
    security_fee = fields.Integer(string='Security Fee', tracking=True)
    registration_fee = fields.Integer(string='Registration Fee')

    company_id = fields.Many2one('res.company', string='Campus',default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.str') or 'New'
        result = super(FeeStructure, self).create(vals)
        return result

    def create_invoice(self, classes, student, date, wiz):
        print('////////',date)
        if student:
            students = [student]
        else:
            students = self.env['op.student'].search([('class_id', 'in', classes.ids)])
        created_ids = []
        for student in students:
            last_month_day = date.replace(
                day=calendar.monthrange(date.year, date.month)[1])

            date_from = date.replace(day=1)
            previos_invoice = self.env['account.move'].search([('student_id','=',student.id),('invoice_date','=',date_from),('move_type','=','out_invoice'),('state','!=','cancel')])
            if previos_invoice or student.state not in ['admitted','fee_defaulter']:
                break
                # raise ValidationError(f'Fee already generated for this month for{student.display_name},,{previos_invoice},,,{date_from}')

            fee_structure = self.env['fee.structure'].search([
                ('classes', '=', student.year_id.id),
                ('date_start', '<=', date),
                ('date_end', '>=', date),
                ('company_id', '>=', student.company_id.id)
            ], limit=1)

            if not fee_structure:
                raise ValidationError('No Fee Structure Defined for the class %s' % student.class_id.name)
            invoice_lines = []

            if not student.id_old_student:

                for line in fee_structure.fee_details:
                    invoice_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'quantity': 1,
                        'price_unit': line.amount,
                        'account_id': line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, line.tax_ids.ids)],  # Adding tax_ids here

                    }))
            else:
                tuition_fee = self.env['product.product'].search(
                    [('name', '=', 'Tuition Fee'), ('is_school_fee', '=', True)])
                invoice_lines.append((0, 0, {
                    'product_id': tuition_fee.id,
                    'quantity': 1,
                    'price_unit': student.amount_fee,
                    'account_id': tuition_fee.property_account_income_id.id or tuition_fee.categ_id.property_account_income_categ_id.id,
                }))


            waiver_product = self.env['product.product'].search(
                [('name', '=', 'Fee Waiver'), ('is_school_fee', '=', True)])
            for waiver in student.tag_ids:
                if waiver.is_admission_discount != True and waiver.is_security_discount != True:
                    invoice_lines.append((0, 0, {
                        'product_id': waiver_product.id,
                        'quantity': 1,
                        'price_unit': -float(waiver.amount),
                        'account_id': waiver_product.property_account_income_id.id or waiver_product.categ_id.property_account_income_categ_id.id,
                    }))

            fee_st = self.env['fee.structure'].search([('classes', '=', student.year_id.id),('company_id', '>=', student.company_id.id)])
            fee_st = fee_structure

            if wiz.admission_fee == True:
                admission_fee = self.env['product.product'].search(
                    [('name', '=', 'Admission Fee'), ('is_school_fee', '=', True)])
                invoice_lines.append((0, 0, {
                    'product_id': admission_fee.id,
                    'quantity': 1,
                    'price_unit': fee_st.admission_fee,
                    'account_id': admission_fee.property_account_income_id.id or admission_fee.categ_id.property_account_income_categ_id.id,
                }))

                waiver_product = self.env['product.product'].search(
                    [('name', '=', 'Admission Waiver'), ('is_school_fee', '=', True)])
                for waiver in student.tag_ids:
                    if waiver.is_admission_discount == True:
                        invoice_lines.append((0, 0, {
                            'product_id': waiver_product.id,
                            'quantity': 1,
                            'price_unit': -float(waiver.amount),
                            'account_id': waiver_product.property_account_income_id.id or waiver_product.categ_id.property_account_income_categ_id.id,
                        }))

                # waiver_product = self.env['product.product'].search(
                #     [('name', '=', 'Security Waiver'), ('is_school_fee', '=', True)])
                # for waiver in student.tag_ids:
                #     if waiver.is_security_discount == True:
                #         invoice_lines.append((0, 0, {
                #             'product_id': waiver_product.id,
                #             'quantity': 1,
                #             'price_unit': -float(waiver.amount),
                #             'account_id': waiver_product.property_account_income_id.id or waiver_product.categ_id.property_account_income_categ_id.id,
                #         }))


            if wiz.annual_charges == True:
                annual_charges = self.env['product.product'].search(
                    [('name', '=', 'Annual Charges'), ('is_school_fee', '=', True)])
                invoice_lines.append((0, 0, {
                    'product_id': annual_charges.id,
                    'quantity': 1,

                    'price_unit': fee_st.annual_charges,
                    'account_id': annual_charges.property_account_income_id.id or annual_charges.categ_id.property_account_income_categ_id.id,
                }))



            if wiz.security_charges == True:
                security_charges = self.env['product.product'].search(
                    [('name', '=', 'Security Charges'), ('is_school_fee', '=', True)])
                invoice_lines.append((0, 0, {
                    'product_id': security_charges.id,
                    'quantity': 1,

                    'price_unit': fee_st.security_fee,
                    'account_id': security_charges.property_account_income_id.id or security_charges.categ_id.property_account_income_categ_id.id,
                }))
                waiver_product = self.env['product.product'].search(
                [('name', '=', 'Security Waiver'), ('is_school_fee', '=', True)])
                _logger.info('Waiver producr')
                _logger.info(waiver_product)
                for waiver in student.tag_ids:
                    _logger.info(waiver.name)
                    if waiver.is_security_discount == True:
                        _logger.info('innn ifffffff')
                        invoice_lines.append((0, 0, {
                            'product_id': waiver_product.id,
                            'quantity': 1,
                            'price_unit': -float(waiver.amount),
                            'account_id': waiver_product.property_account_income_id.id or waiver_product.categ_id.property_account_income_categ_id.id,
                        }))
            if wiz.registration_fee == True:
                registration_fee = self.env['product.product'].search(
                    [('name', '=', 'Registration Fee'), ('is_school_fee', '=', True)])
                invoice_lines.append((0, 0, {
                    'product_id': registration_fee.id,
                    'quantity': 1,

                    'price_unit': fee_st.registration_fee,
                    'account_id': registration_fee.property_account_income_id.id or registration_fee.categ_id.property_account_income_categ_id.id,
                }))
            # if wiz.fee_arrears == True:
            fee_arrears_recs = self.env['op.fee.opining'].search([('student_id','=',student.id),('status','!=','Paid')])
            amt_s = sum(fee_arrears_recs.mapped('amount'))
            if sum(fee_arrears_recs.mapped('amount')) > 0:
                for rr in fee_arrears_recs:
                    rr.status = 'Paid'

                fee_arrears = self.env['product.product'].search(
                    [('name', '=', 'Fee Arrears'), ('is_school_fee', '=', True)])
                invoice_lines.append((0, 0, {
                    'product_id': fee_arrears.id,
                    'quantity': 1,

                    'price_unit': sum(fee_arrears_recs.mapped('amount')),
                    'account_id': fee_arrears.property_account_income_id.id or fee_arrears.categ_id.property_account_income_categ_id.id,
                }))

            # arrears = self.env['account.move'].search([('partner_id','=',student.partner_id.id),('invoice_date_due','<',date),('state','=','posted'),('payment_status','!=','partial')])
            # arrears_amount = sum(arrears.mapped('amount_residual'))
            # for arrear in arrears:
            #     arrear.button_cancel()

            # arrears_product = self.env['product.product'].search([('name', '=', 'Fee Arrears'),('is_school_fee', '=',True)])
            # if arrears_amount > 0:
            #     invoice_lines.append((0, 0, {
            #         'product_id': arrears_product.id,
            #         'quantity': 1,
            #         'price_unit': arrears_amount,
            #         'account_id': arrears_product.property_account_income_id.id or arrears_product.categ_id.property_account_income_categ_id.id,
            #     }))

            arrears = self.env['account.move'].search([('partner_id','=',student.partner_id.id),('invoice_date_due','<',date),('state','=','posted'),
                                                       ('payment_state','in',['not_paid']),('move_type','=','out_invoice')])
            arrears_amount = sum(arrears.mapped('amount_residual'))
            for arrear in arrears:
                arrear.button_cancel()
                arrear.block_invoice()


            arrears_product = self.env['product.product'].search([('name', '=', 'Fee Arrears'),('is_school_fee', '=',True)])
            if arrears_amount > 0:
                invoice_lines.append((0, 0, {
                    'product_id': arrears_product.id,
                    'quantity': 1,
                    'price_unit': arrears_amount,
                    'account_id': arrears_product.property_account_income_id.id or arrears_product.categ_id.property_account_income_categ_id.id,
                }))


            invoice_vals = {
                'partner_id': student.partner_id.id,
                'student_id': student.id,
                'move_type': 'out_invoice',
                'invoice_date': date,
                'invoice_date_due': date + timedelta(days=7),
                'company_id': student.company_id.id,
                'is_fee_invoice': True,

                'journal_id': self.env['account.journal'].search([('company_id', '=', student.company_id.id), ('type',
                                                                                                               'in',
                                                                                                               [
                                                                                                                   'sale'])],
                                                                 limit=1).id,
                'invoice_line_ids': invoice_lines,
            }
            print(invoice_vals)

            id= (self.env['account.move'].create(invoice_vals))
            id.action_post()
            created_ids.append(id.id)

        return created_ids

class FeeDetails(models.Model):
    _name = 'fee.details'
    _description = 'Fee Details'

    structure_id = fields.Many2one('fee.structure', string='Fee Structure', copy=True)
    product_id = fields.Many2one('product.product', string='Fee Head', copy=True,
                                 domain="[('is_school_fee', '=',True)]")
    tax_ids = fields.Many2many('account.tax', string='Taxes', domain="[('type_tax_use', '=','sale')]")
    amount = fields.Float('Amount', copy=True)
