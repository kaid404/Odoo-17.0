from odoo import models, fields


class OpParentRelation(models.Model):
    _name = "op.parent.relationship"
    _description = "Relationships"

    name = fields.Char('Name', required=True)
