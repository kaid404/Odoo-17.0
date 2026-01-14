# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    sales_tax = fields.Boolean(string="Sales Tax")
