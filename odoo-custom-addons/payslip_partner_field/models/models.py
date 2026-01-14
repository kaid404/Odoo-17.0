from odoo import models, fields, api


class PayslipPartnerField(models.Model):
    _inherit = 'hr.salary.rule'

    partner_check = fields.Boolean(string='Show Partner ID')


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip.line'

    partner_id_field = fields.Many2one('res.partner', compute='get_partner_id', string='Partner')

    @api.depends('employee_id', 'salary_rule_id', 'salary_rule_id.partner_check')
    def get_partner_id(self):
        for line in self:
            if line.salary_rule_id and line.salary_rule_id.partner_check:
                if line.employee_id:
                    line.partner_id_field = line.employee_id.work_contact_id
                else:
                    line.partner_id_field = False
            else:
                line.partner_id_field = False

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _action_create_account_move(self):
        res = super()._action_create_account_move()

        for slip in self:
            if not slip.move_id:
                continue

            partner_map = {}
            for line in slip.line_ids:
                if line.salary_rule_id.partner_check and line.partner_id_field:
                    amount = line.amount
                    partner_map[(line.name, amount)] = line.partner_id_field.id

            for move_line in slip.move_id.line_ids:
                key = (move_line.name, abs(move_line.debit - move_line.credit))
                if key in partner_map and not move_line.partner_id:
                    move_line.partner_id = partner_map[key]

        return res