from odoo import models, fields, api


class RestrictedField(models.Model):
    _inherit = 'account.account'

    restricted = fields.Boolean(string='Restrict')

