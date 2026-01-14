from odoo import fields, models, api


class Attendance(models.Model):
    _inherit="hr.attendance"


    @api.constrains('employee_id','check_in')
    def check_for_absent_deduction(self):
        for rec in self:
            employee = rec.employee_id
            att_date = rec.check_in.date() if rec.check_in else False

            if not (employee and att_date):
                continue

            absent_recs = self.env['absent.deduction.lines'].search([
                ('employee_id', '=', employee.id),
                ('absent_date', '=', att_date),
            ], limit=1)
            if absent_recs:
                absent_recs.unlink()

            # for absent in absent_recs:
            #     line_to_delete = absent.line_ids.filtered(lambda l: l.date == att_date)
            #     if line_to_delete:
            #         line_to_delete.unlink()



class Leave(models.Model):
    _inherit="hr.leave"

    def action_approve(self):
        res = super(Leave, self).action_approve()
        for rec in self:
            employee = rec.employee_id
            date = rec.date_from if rec.date_from else False

            if not (employee and date):
                continue


            absent_recs = self.env['absent.deduction.lines'].search([
                ('employee_id', '=', employee.id),
                ('absent_date', '=', date),
            ], limit=1)
            if absent_recs:
                absent_recs.unlink()

        return res






