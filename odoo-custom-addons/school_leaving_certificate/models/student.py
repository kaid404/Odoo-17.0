from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import date,timedelta

class StudentFee(models.Model):
    _inherit = 'op.student'

    slc_id = fields.Many2one('school.leaving.certificate', string='School Leaving Certificate', store=True)


    def action_create_slc_certificate(self):
        for rec in self:
            vals = {
                'name': "New",
                'date': fields.Date.today(),
                'student_id': rec.id,
                'state': 'draft',
                'gender': rec.gender,
                'father_name': rec.name,
                'class_id': rec.year_id.id,
                'section_id': rec.section_id.id,
                'gr_no': rec.gr_no,
                'admission_no': rec.gr_no,
                'roll_no': rec.gr_no,
                'reason_leaving': "",
                'possible_attendance': '',
                'student_attendance': '',
                'fee_due': '',
                'enrollment_date': False,
                'phone_no': rec.mobile,
                'mobile_no': rec.mobile,
                'street': rec.street,
                'street2': rec.street2,
                'city': rec.city,
                'state_id': rec.state_id.id,
                'zip': rec.zip,
                'country_id': rec.country_id.id,
                'company_id': rec.company_id.id,
            }
            slc_id = self.env['school.leaving.certificate'].create(vals)
            rec.write({
                'slc_id': slc_id.id,
            })
        return self.get_slc()

    def get_slc(self):
        action = self.env.ref('school_leaving_certificate.action_school_leaving_certificate_form').read()[0]
        action['domain'] = [('student_id', 'in', self.ids)]
        return action

    def create_credit_note(self):
        vals = {
            'partner_id': self.partner_id.id,
            'student_id': self.id,
            'move_type': 'out_refund',
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today(),
            'journal_id': self.env['account.journal'].search([('company_id', '=', self.company_id.id), ('type','in',['sale'])],limit=1).id or False,
            'invoice_line_ids': [(0,0,{
            'product_id': self.env['product.product'].search([('name', '=', 'Security Charges')]).id or False,
            'quantity': 1,
            'price_unit': self.env['fee.structure'].search([('classes', '=', self.class_id.id)]).security_fee or 0,
        })],
        }
        credit_note_id = self.env['account.move'].create(vals)
        if credit_note_id:
            return self.open_credit_note(move_id=credit_note_id.id)


    def open_credit_note(self,move_id):
        action = self.env.ref('school_leaving_certificate.action_student_move_out_refund_type').read()[0]
        action['domain'] = [('id', '=', move_id)]
        return action


