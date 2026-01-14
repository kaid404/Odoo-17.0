from email.policy import default
from num2words import num2words
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime,timedelta,date
import calendar

class SchoolLeavingCertificate(models.Model):
    _name = 'school.leaving.certificate'
    _description = 'School Leaving Certificate'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=False, readonly=True, default='New', store=True)
    date = fields.Date('Leaving Date', store=True, copy=False,default=fields.Date.today())
    student_id = fields.Many2one('op.student', string="Student")
    state = fields.Selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],string="Status",default="draft")
    gender = fields.Selection([('m','Male'),('f','female'),('o','Other')],string="Gender")
    father_name = fields.Char(string="Father")
    class_id = fields.Many2one('op.academic.year', string='Class', store=True)
    section_id = fields.Many2one('class.section', string='Section', store=True)
    gr_no = fields.Char(string='Registration No')
    admission_no = fields.Char(string='Admission No')
    roll_no = fields.Char(string='Roll No')
    reason_leaving = fields.Char(string="Reason for Leaving")
    possible_attendance = fields.Char(string="Possible Attendance")
    student_attendance = fields.Char(string="Student's Attendance")
    fee_due = fields.Char(string="Due/Fee Paid Upto")
    enrollment_date = fields.Date('Enrollment Date', store=True, copy=False,default=fields.Date.today())
    phone_no = fields.Char(string='Phone No')
    mobile_no = fields.Char(string='Mobile No')
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    city = fields.Char(string="City")
    state_id = fields.Many2one('res.country.state',string="State")
    zip = fields.Char(string="zip")
    country_id = fields.Many2one('res.country',string="Country")
    company_id = fields.Many2one('res.company',string="Campus")
    move_id = fields.Many2one('account.move',string="Move")

    @api.model
    def format_date(self, input_date):
        """
        Format the input date into the format (11 Nov 2024).
        """
        if input_date:
            try:
                # Ensure input_date is a datetime object
                if isinstance(input_date, str):
                    input_date = datetime.strptime(input_date, "%Y-%m-%d")

                # Format the date as '11 Nov 2024'
                formatted_date = input_date.strftime("%d %b %Y")
                return formatted_date
            except Exception as e:
                return f"Error: {e}"
        return "No Date Available"

    @api.model
    def birth_date_to_words(self, birth_date):
        """
        Convert the full date of birth to words (day, month, year).
        """
        if birth_date:
            try:
                birth_day = birth_date.day
                birth_month = birth_date.month
                birth_year = birth_date.year
                day_in_words = num2words(birth_day, lang='en').capitalize()
                month_in_words = num2words(birth_month, lang='en').capitalize()
                year_in_words = num2words(birth_year, lang='en').capitalize()
                dob_in_words = f"{day_in_words} {month_in_words} {year_in_words}"
                return dob_in_words.upper()
            except Exception as e:
                return f"Error: {e}"
        return "No Birth Date Available"

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.slc.student') or 'New'
        result = super(SchoolLeavingCertificate, self).create(vals)
        return result

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_confirm(self):
        self.create_credit_note()
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def create_credit_note(self):
        vals = {
            'partner_id': self.student_id.partner_id.id,
            'student_id': self.student_id.id,
            'move_type': 'out_refund',
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today(),
            'journal_id': self.env['account.journal'].search([('company_id', '=', self.student_id.company_id.id), ('type','in',['sale'])],limit=1).id or False,
            'slc_id': self.id,
            'invoice_line_ids': [(0,0,{
            'product_id': self.env['product.product'].search([('name', '=', 'Security Charges')]).id or False,
            'quantity': 1,
            'price_unit': self.env['fee.structure'].search([('classes', '=', self.class_id.id),('company_id', '=', self.student_id.company_id.id)]).security_fee or 0,
        })],
        }
        credit_note_id = self.env['account.move'].create(vals)
        self.move_id = credit_note_id.id
        if self.move_id:
            return self.open_credit_note()

    def open_credit_note(self):
        action = self.env.ref('school_leaving_certificate.action_student_move_out_refund_type').read()[0]
        action['domain'] = [('slc_id', 'in', self.ids)]
        return action
