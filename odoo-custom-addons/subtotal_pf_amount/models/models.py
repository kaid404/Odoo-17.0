from odoo import fields, models, api

class EmployeeEmployer(models.Model):
    _inherit = 'pf.employee.employer'


    subtotal_amount = fields.Float(string="Total PF", compute="get_total_pf")

    @api.onchange('pf_employee_amount', 'pf_employer_amount', 'total_amount_profit', 'total_opening')
    def get_total_pf(self):
        for rec in self:
            rec.subtotal_amount = rec.pf_employee_amount + rec.pf_employer_amount + rec.total_amount_profit + rec.total_opening