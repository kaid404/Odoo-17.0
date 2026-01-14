# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class PriceList(models.Model):
    _inherit = 'product.pricelist'

    mrp = fields.Boolean(string="MRP")
    tp = fields.Boolean(string="TP")
    retailer_price = fields.Boolean(string="Retailer Price")
    wholesale_price = fields.Boolean(string="Wholesaler Price")
