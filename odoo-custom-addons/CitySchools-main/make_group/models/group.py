from odoo import models, fields, api


class MakeGroup(models.Model):
    _inherit = 'account.move'
    _description = "Account Move"


