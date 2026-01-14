from odoo import models, fields


class OpPublisher(models.Model):
    _name = "op.publisher"
    _description = "Publisher"

    name = fields.Char('Name', size=20, required=True)
    address_id = fields.Many2one('res.partner', 'Address')
    media_ids = fields.Many2many('op.media', string='Media(s)')
