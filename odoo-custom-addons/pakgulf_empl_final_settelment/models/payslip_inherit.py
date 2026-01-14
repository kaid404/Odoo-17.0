from odoo import models, fields, api
import calendar


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Hr Payslip'

    final_settlement_id = fields.Many2one('employee.final.settlement', string="Final Settlement")
    emp_bank_name = fields.Char(string='Employee Bank Nam', readonly=True)
    emp_acc_no = fields.Char(string='Account #', readonly=True)
    last_work_date = fields.Date(string='Last Working Date', readonly=True)
    count_days = fields.Integer(string='Worked Days', readonly=True)
    total_days_in_month = fields.Integer(
        string='Total Days in Month',
        compute='_compute_total_days_in_month',
        store=True
    )

    @api.depends('last_work_date')
    def _compute_total_days_in_month(self):
        for payslip in self:
            if payslip.last_work_date:
                year = payslip.last_work_date.year
                month = payslip.last_work_date.month
                total_days = calendar.monthrange(year, month)[1]
                payslip.total_days_in_month = total_days
            else:
                payslip.total_days_in_month = 0

    def action_payslip_paid(self):
        for payslip in self:
            payslip.state = 'paid'
            if payslip.final_settlement_id and payslip.final_settlement_id.state == 'payslip':
                payslip.final_settlement_id.write({'state': 'paid'})
        return True
