from odoo import models, fields, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Hr Contract'

    final_settlement_structure = fields.Many2one('hr.payroll.structure.type', string='Final Settlement Structure Type')


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'
    _description = 'Hr Payroll Structure Type'

    check = fields.Boolean(string='Final Settlement')
