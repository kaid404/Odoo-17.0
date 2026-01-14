from odoo import models, fields, api
from datetime import datetime, time, timedelta, date
from odoo.exceptions import ValidationError, UserError


class AttendancePoliy(models.Model):
    _name = "gxs.late.policy.dep"
    _description = "Late Policy"
    _rec_name = "user"
    # convert_to_display_name
    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    time = fields.Float(string='Late Deduction', required=True)
    early_time = fields.Float(string='Early Departure Deduction', required=True)
    per_month = fields.Integer(string='Deduct After Day(s)', required=True)
    on_each = fields.Integer(string='For Leave deduction On Each late', required=True)
    on_each_for_salary = fields.Integer(string='For Salary deduction On Each late', required=True)
    regular_shift = fields.Float(string='MIN Regular Shift Time', required=True)
    half_day_shift = fields.Float(string='MIN Half Day Shift Time', required=True)
    # on_each = fields.Integer(string='On Each late', required=True)
    department_ids = fields.Many2many('hr.department', string='Department')
    user = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user, readonly=True)

    leave_ids = fields.One2many('gxs.leave.deduction.policy', 'late_policy_id', string="Leaves")


    late_leave_ids = fields.Many2many('hr.leave.type', string="Leaves")


    type = fields.Selection(
        [
            ("by_depart", "By depart"),
            ("global", "Global"),

        ], default='by_depart',
        string="Type",)

    @api.onchange('department_ids')
    def onchange_work(self):
        print('work')
        li = []
        for c in self.department_ids:
            i = c.id
            con = 0
            i = str(i)
            for a in i:
                con = con + 1
                if a == '=':
                    id = int(i[con:-1])
                    li.append(id)
        dep = self.env['gxs.late.policy.dep'].search(
            [('department_ids', 'in', li), ('date_from', '>=', date.today()), ('date_from', '<=', date.today())])
        if dep and self.department_ids:
            raise ValidationError('Department already exit')


class AttendancePolicy(models.Model):
    _name = "gxs.leave.deduction.policy"
    _description = "Leave Policy"

    late_policy_id = fields.Many2one('gxs.late.policy.dep')
    leave_id = fields.Many2one('hr.leave.type', string="Leave")
    leave_id_copy = fields.Many2one('hr.leave.type', string="Leave")
    deduct_from = fields.Float('>=')
    deduct_to = fields.Float('<=')
    deduction = fields.Float('Deduction')


class AttendancePolicyHoliday(models.Model):
    _inherit = "hr.leave.type"

    is_unpaid = fields.Boolean(string="Is Unpaid?")

    late_leave_ids = fields.One2many('gxs.leave.deduction.policy', 'leave_id_copy', string="Leaves")

    @api.onchange('is_unpaid')
    def _onchange_is_unpaid(self):
        print("LLLLLLLLLLL")
        if self.is_unpaid:
            existing_unpaid_record = self.env['hr.leave.type'].search([('is_unpaid', '=', True),])

            if len(existing_unpaid_record) >= 1:
                raise ValidationError("Only one record can have 'Is Unpaid' set to True.")
