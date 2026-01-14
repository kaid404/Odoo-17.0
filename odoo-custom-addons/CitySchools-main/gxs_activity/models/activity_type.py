from odoo import models, fields


class OpActivityType(models.Model):
    _name = "op.activity.type"
    _description = "Activity Type"

    name = fields.Char('Name', size=128, required=True)
    active = fields.Boolean(default=True)
