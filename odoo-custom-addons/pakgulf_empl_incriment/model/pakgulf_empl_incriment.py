from odoo import models, fields, api, _


class EmployeeIncrementWizard(models.TransientModel):
    _name = 'employee.increment.wizard'
    _description = 'Employee Increment Wizard'

    @api.model
    def _post_active_users(self):
        if self.env.context.get('active_model', False) == 'hr.contract' and self.env.context.get('active_ids', False):
            active_users = self.env['hr.contract'].browse(self.env.context['active_ids'])
            employee_lines = []
            for user in active_users:
                employee_lines.append((0, 0, {'employee_id': user.employee_id.id}))
            return employee_lines

    employee_ids = fields.One2many('hr.employee.increment.line', 'wizard_id', string='Employees',
                                   default=_post_active_users)
    contract_id = fields.Many2one('hr.contract', string='Contract')

    def apply_increment(self):
        increment_details = []
        for line in self.employee_ids:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', line.employee_id.id), ('state', '=', 'open')])
            if line.amount:
                if contract:
                    wage = contract.wage
                    contract.write({'wage': contract.wage + line.amount})
                    print('detail_lines', contract.increment_detail_ids)
                    # Create increment detail record
                    increment_detail = self.env['hr.employee.increment.lines'].create({
                        'employee_id': line.employee_id.id,
                        'date': line.date,
                        'amount': line.amount,
                        'contract_id': contract.id,
                        'wage': wage,
                    })
                    increment_details.append(increment_detail.id)


class EmployeeIncrementLine(models.TransientModel):
    _name = 'hr.employee.increment.line'
    _description = 'Employee Increment Line'

    wizard_id = fields.Many2one('employee.increment.wizard', string='Wizard')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr.contract', string='Contract')
    date = fields.Date(string='Date')
    wage = fields.Float(string="Wage")
    amount = fields.Float(string='Amount')


class EmployeeIncrementLines(models.Model):
    _name = 'hr.employee.increment.lines'
    _description = 'Employee Increment Line'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr.contract', string='Contract')
    date = fields.Date(string='Date')
    wage = fields.Float(string="Wage")
    amount = fields.Float(string='Amount')

    def unlink(self):
        for record in self:
            if record.contract_id and record.amount:
                # Rollback wage
                new_wage = record.contract_id.wage - record.amount
                record.contract_id.write({'wage': new_wage})
        res = super(EmployeeIncrementLines, self).unlink()
        return res


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    increment_detail_ids = fields.One2many('hr.employee.increment.lines', 'contract_id', string='Increment Details')
    employee_ids = fields.One2many('hr.employee', 'contract_id', string='Employees')

    def action_register_cpr(self):
        return {
            'name': _('Employee Increment'),
            'res_model': 'employee.increment.wizard',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
