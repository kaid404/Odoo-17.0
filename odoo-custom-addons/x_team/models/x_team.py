from odoo import models, fields

class XTeam(models.Model):
    _name = 'x_team'
    _description = 'Team'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Team', required=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    x_studio_team = fields.Many2one(
        'x_team',
        string='Team'
    )
