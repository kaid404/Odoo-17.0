# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    retailer_or_wholesaler = fields.Selection([
        ('retailer', 'Retailer'),
        ('wholesaler', 'Wholesaler'),
        ('none', 'None'),
    ], string="Customer Type", default='none')


class Stock(models.Model):
    _inherit = 'stock.move.line'

    expired_date = fields.Datetime(string="Expiration Date ", related="lot_id.expiration_date")
