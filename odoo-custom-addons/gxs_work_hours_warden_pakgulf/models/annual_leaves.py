from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError, MissingError
from datetime import datetime


# class Unpaid(models.Model):
#     _inherit = 'hr.leave'
#     # def action_refuse(self):
#     #     res = super(Unpaid, self).action_refuse()
#     #
#     #     if 'Early Leave Deduction' in self.name:
#     #         leave_id = self.env['hr.leave.type'].search(
#     #             [('name', '=', 'Unpaid'), ('company_id', '=', self.employee_id.company_id.id)])
#     #         id = self.env['hr.leave'].create({
#     #             'employee_id': self.employee_id.id,
#     #             'date_from': self.date_from,
#     #             'date_to': self.date_to,
#     #             'request_date_from': self.request_date_from,
#     #             'request_date_to': self.request_date_to,
#     #             'holiday_status_id': leave_id.id,
#     #             'number_of_days': self.number_of_days,
#     #             'name': 'Unpaid Leave',
#     #
#     #         })
#     #
#     #     return res

class AnnualLeaves(models.Model):
    _inherit = 'hr.leave.allocation'

    def action_el_leave_refuse(self):
        for rec in self:
            current_date = datetime.now().date()
            years = 0
            if rec.date_from and rec.holiday_status_id.id == 13:
                date_from = fields.Date.from_string(rec.date_from)
                years = current_date.year - date_from.year
                if years >= 2:
                    rec.action_refuse()

    def action_validate(self):
        current_date = datetime.now().date()
        wage = self.env["hr.contract"].search(
            [('employee_id', '=', self.employee_id.id),('state','=','open')
             ], limit=1, order='id desc')
        years = 0
        if wage.date_start:
            date_start = fields.Date.from_string(wage.date_start)
            years = current_date.year - date_start.year
            print('[[[[[[[[[[[[[[[[[[')
            if years < 1 and self.holiday_status_id.id == 14:
                raise ValidationError(
                    f"This allocation can't be approve now")

        print(f'Total number of years: {years}')
        print("emplo23344yee", self.holiday_status_id)
        for t in self:
            if t.holiday_status_id.name == 'Annual Leave':
                for rac in t.employee_ids:
                    print(rac.name)
                    permanent = self.env["hr.contract.history"].search(
                        [('employee_id', '=', rac.id)
                         ])
                    state = 0
                    for i in permanent.contract_ids:
                        if i.state == 'open' and i.date_end == False:
                            state = 1
                        print(i.date_end)
                        print(i.state)

                    if state == 0:
                        raise ValidationError(
                            f"{rac.name} is not permanent only permanent employee can apply for Annual leave")

                res =  super(AnnualLeaves, self).action_validate()
                self.count_leaves_leaves_action()
                return res
            else:

                res = super(AnnualLeaves, self).action_validate()
                self.count_leaves_leaves_action()
                return res