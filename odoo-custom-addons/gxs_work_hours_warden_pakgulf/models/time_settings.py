from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AttendancePoliy(models.Model):
    _name = "kt.atten.policy"
    _rec_name = "user"
    time = fields.Float(string='Time', required=True)

    user = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user, readonly=True)

    # @api.constrains('department_id')
    # def check_cnic_num(self):
    @api.model
    def create(self, vals_list):
        print("worsdncvjksdbvikdsbvkbdsjvrey'''''''''''''''''''''''''''''''''''''''''''''''''")
        time = self.env["kt.atten.policy"].search([])
        print(time, self.id)
        # for times in time:
        #     if times.id != 1:
        #         raise ValidationError("You are not Allow to multiple relax policy")

        res = super(AttendancePoliy, self).create(vals_list)
        time = self.env["kt.atten.policy"].search([])
        print(time)
        for times in time:
            if times.id != 1:
                times.unlink()
                raise ValidationError("You are not Allow to multiple relax policy")

        return res
