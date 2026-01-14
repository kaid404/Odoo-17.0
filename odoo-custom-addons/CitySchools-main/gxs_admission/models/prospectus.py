from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class OpAdmission(models.Model):
    _name = "op.prospectus"

    application_id = fields.Many2one('op.admission',string='Application')
    applicant_name = fields.Char(string='Applicant Name')
    father_name = fields.Char(string='Guardian/Father Name')
    guardian_cnic = fields.Char(string='Guardian/Father CNIC')
    company_id = fields.Many2one('res.company')
    register_id = fields.Many2one('op.admission.register',string="Register")
    amount = fields.Float(string='Amount')

