from odoo import models, fields, api


class LateCheckIn(models.Model):
    _inherit = 'late.check_in'


    amount = fields.Float(string="%Day")