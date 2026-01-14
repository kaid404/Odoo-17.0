from odoo import models, fields


class OpAsset(models.Model):
    _name = "op.asset"
    _description = "Classroom Assets"

    asset_id = fields.Many2one('op.classroom', 'Asset')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    code = fields.Char('Code', size=256)
    product_uom_qty = fields.Float('Quantity', required=True)
