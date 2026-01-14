from odoo import models, fields, api


class FinalSettlementCheck(models.Model):
    _inherit = 'hr.contract'

    final_settlement = fields.Boolean(string='Final Settlement')

class HrEmployee(models.Model):
    _inherit = 'employee.final.settlement'

    def action_payslip(self):
        res = super().action_payslip()

        for rec in self:
            contracts = self.env['hr.contract'].search([('employee_id', '=', rec.name.id)])
            for contract in contracts:
                contract.final_settlement = True

        return res

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_employees(self):
        employees = super()._get_employees()

        filtered_employees = employees.filtered(
            lambda emp: not emp.contract_id or not emp.contract_id.final_settlement
        )
        return filtered_employees


