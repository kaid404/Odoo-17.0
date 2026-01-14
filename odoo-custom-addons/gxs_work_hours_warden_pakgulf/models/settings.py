from odoo import fields, models, api

class ResConfigSettingsKaytax(models.TransientModel):
    _inherit = 'res.config.settings'

    relax_time = fields.Integer(string='Relax Time',default=15,config_parameter='kaytex.relax_time')

    @api.model
    def set_values(self):
        res = super(ResConfigSettingsKaytax, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('relax_time', self.relax_time)

        return res
