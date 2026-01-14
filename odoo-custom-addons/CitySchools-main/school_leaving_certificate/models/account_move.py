from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import date,timedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    slc_id = fields.Many2one('school.leaving.certificate', string='School Leaving Certificate', store=True)

