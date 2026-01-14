from odoo import models, fields


class OpTag(models.Model):
    _name = "op.tag"
    _description = "Media Tags"

    name = fields.Char('Name', size=64, required=True)
