from odoo import models,fields,api

class ProductsFormInherit(models.Model):
    _inherit = 'product.product'

    is_school_fee = fields.Boolean(string='Is school fee?')


