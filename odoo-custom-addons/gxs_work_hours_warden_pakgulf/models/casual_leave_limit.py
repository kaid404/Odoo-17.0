from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CasualLeaveLimit2(models.Model):
    _inherit = 'hr.leave'

    def action_approve(self):

        res  = super(CasualLeaveLimit2, self).action_approve()

        late_d = self.env['rst.late.count'].search(
            [('employee_id', '=', self.employee_id.id),
             ('date', '=', self.request_date_from),
             ]).unlink()
        return res
class CasualLeaveLimit(models.Model):
    _inherit = 'hr.leave.allocation'

    @api.model
    def create(self, values):
        print("holiday status id")
        # Check if the leave type is casual leave and the employee is not on a permanent contract
        leave_id = self.env['hr.leave.type'].search(
            [('name', '=', 'Casual Leave')])
        if values.get('holiday_status_id') == leave_id.id:
            employee_id = values.get('employee_id')
            if employee_id:
                employee = self.env['hr.employee'].browse(employee_id)
                print("employee.contract_id.contract_type_id",employee.contract_id.contract_type_id)
                if employee.contract_id and employee.contract_id.contract_type_id.name == 'Permanent':
                    print("values.get('number_of_days_display')", values.get('number_of_days_display'))
                    if values.get('number_of_days_display') > 10:
                        raise ValidationError(
                            "Cannot allocate more than 10 casual leaves for permanent contract employees.")
                else:
                    raise ValidationError(
                            "Cannot allocate casual leaves for non-permanent contract employees.")
        return super(CasualLeaveLimit, self).create(values)
