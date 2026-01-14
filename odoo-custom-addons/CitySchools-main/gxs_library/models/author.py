from odoo import models, fields


class OpAuthor(models.Model):
    _name = "op.author"
    _description = "Media Author"

    name = fields.Char('Name', size=128, required=True)
    address = fields.Many2one('res.partner', 'Address')
    media_ids = fields.Many2many('op.media', string='Media(s)')
