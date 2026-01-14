from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GlobalInput(models.Model):
    _inherit = 'global.input'

    show_day_field = fields.Boolean(string="Absent Deduction", default=False, store=True)
    hide_day_field = fields.Boolean(string="Hide Day Field", compute="_compute_hide_day_field")
    hide_calculate_button = fields.Boolean(string="Hide Button",default=False)

    def calculate_absent(self):
        for rec in self:
            for line in rec.input_line_ids:
                line.calculate_amount_through_days()
            rec.hide_calculate_button = True

    @api.depends('apply_by')
    def _compute_hide_day_field(self):
        for rec in self:
            rec.hide_day_field = rec.apply_by in ('batch', 'dpt', 'comp')

    def add_inputs(self):
        list = []
        input_list = {}
        if self.batch_id:
            batch_payslip = self.env['hr.payslip'].search(
                [('payslip_run_id', '=', self.batch_id.id), ('date_to', '<=', self.date_to),
                 ('date_from', '>=', self.date_from),
                 ('state', 'not in', ['done', 'refuse', 'paid'])])
            print(batch_payslip)
            for rec in self.input_line_ids:
                input_list = \
                    (0, 0, {
                        "name": rec.name,
                        "input_type_id": rec.input_type_id.id,
                        "sequence": rec.sequence,
                        "code": rec.code,
                        "amount": rec.amount

                    })
                list.append(input_list)
            print(list)
            for slips in batch_payslip:
                print(slips)
                slips.write({"input_line_ids": list})
                slips.compute_sheet()
            self.state = 'done'

        elif self.company_id:
            cop_payslip = self.env['hr.payslip'].search(
                [('company_id', '=', self.company_id.id), ('state', '=', 'verify')])
            for rec in self.input_line_ids:
                input_list = \
                    (0, 0, {
                        "name": rec.name,
                        "input_type_id": rec.input_type_id.id,
                        "sequence": rec.sequence,
                        "code": rec.code,
                        "amount": rec.amount

                    })
                list.append(input_list)
            print(list)
            for slips in cop_payslip:
                print(slips)
                slips.write({"input_line_ids": list})
                slips.compute_sheet()
            self.state = 'done'


        elif self.department_id:
            dep_payslip = self.env['hr.payslip'].search(
                [('department_id', '=', self.contract_id.department_id.id), ('state', '=', 'verify')])
            for rec in self.input_line_ids:
                input_list = \
                    (0, 0, {
                        "name": rec.name,
                        "input_type_id": rec.input_type_id.id,
                        "sequence": rec.sequence,
                        "code": rec.code,
                        "amount": rec.amount

                    })
                list.append(input_list)
            print(list)
            for slips in dep_payslip:
                print(slips)
                slips.write({"input_line_ids": list})
                slips.compute_sheet()
            self.state = 'done'

        elif self.apply_by == 'emp':
            for rec in self.input_line_ids:
                emp_payslip = self.env['hr.payslip'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'verify')])

                input_vals = {
                    "name": rec.name,
                    "input_type_id": rec.input_type_id.id,
                    "sequence": rec.sequence,
                    "code": rec.code,
                    "amount": rec.amount,
                }

                for slip in emp_payslip:
                    existing_input = slip.input_line_ids.filtered(lambda l: l.code == rec.code)

                    if existing_input:
                        slip.write({'input_line_ids': [(1, existing_input.id, input_vals)]})
                    else:
                        slip.write({'input_line_ids': [(0, 0, input_vals)]})

                    slip.compute_sheet()
            self.state = 'done'

        else:
            raise ValidationError(_('Unable to find any payslip to perform action on.'))


        # for rec in self:
        #     if rec.apply_by == 'emp':
        #         for line in rec.input_line_ids:
        #             payslips = self.env['hr.payslip'].search([
        #                 ('employee_id', '=', line.employee_id.id),
        #                 ('state', '=', 'verify')
        #             ])
        #             for slip in payslips:
        #                 existing_input = slip.input_line_ids.filtered(lambda l: l.code == line.code)
        #
        #                 input_vals = {
        #                     "name": line.name,
        #                     "input_type_id": line.input_type_id.id,
        #                     "sequence": line.sequence,
        #                     "code": line.code,
        #                     "amount": line.amount,
        #                 }
        #
        #                 if existing_input:
        #                     updates = [(1, line.id, input_vals) for line in existing_input]
        #                     slip.write({'input_line_ids': updates})
        #                 else:
        #                     slip.write({
        #                         'input_line_ids': [(0, 0, input_vals)]
        #                     })
        #
        # self.state = 'done'


class GlobalInputLines(models.Model):
    _inherit = 'global.input.line'

    input_days = fields.Integer(string="Days", store=True)

    def calculate_amount_through_days(self):
        date_from = self.input_id.date_from
        date_to = self.input_id.date_to
        emp_id = self.employee_id
        input_days = self.input_days

        if emp_id and date_from and date_to:
            days = (date_to - date_from).days + 1

            running_contract = emp_id.contract_id.filtered(lambda c: c.state == 'open')

            if running_contract:
                monthly_wage = running_contract.wage

                daily_wage = monthly_wage / days

                self.amount = daily_wage * input_days
