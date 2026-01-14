from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class AttendanceAdjustment(models.Model):
    _name = 'attendance.adjustment'
    _description = 'Attendance Adjustment Request'
    _inherit = ['hr.attendance', 'mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', string='Employee')
    worked_hours = fields.Float(string='Worked Hours', compute='get_worked_hours', store=True)
    att_date = fields.Date(string="Attendance Date", tracking=True)
    pre_check_in = fields.Datetime(string="Previous Check In", tracking=True)
    emp_check_in = fields.Datetime(string="Actual Check In", tracking=True)
    pre_check_out = fields.Datetime(string="Previous Check Out")
    emp_check_out = fields.Datetime(string="Actual Check Out")

    state = fields.Selection(
        [('draft', 'Draft'), ('to_be_approved', 'Request'), ('approve', 'Approved'),
         ('refuse', 'Refused'), ('done', 'Done')], readonly=True, default='draft', copy=False, string="Status", tracking=True)
    notes = fields.Text(string='Reason')
    responsible_id = fields.Many2one('res.users', string="Approver", related='employee_id.parent_id.user_id')
    attendance_count = fields.Integer(string='Attendances', compute='get_attendance_count')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company,index=True,required=True)

    @api.depends('emp_check_in', 'emp_check_out')
    def get_worked_hours(self):
        for rec in self:
            if rec.emp_check_in and rec.emp_check_out:
                duration = rec.emp_check_out - rec.emp_check_in
                rec.worked_hours = duration.total_seconds() / 3600
            else:
                rec.worked_hours = 0

    def revert_button(self):
        for rec in self:
            attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '=', rec.emp_check_in),
                ('check_out', '=', rec.emp_check_out),
            ], limit=1)

            if not attendance:
                raise ValidationError(f"No matching attendance found for {rec.employee_id.name} 🕵️‍♂️")

            if not rec.pre_check_in and not rec.pre_check_out:
                attendance.unlink()
                rec.state = 'draft'
            else:
                attendance.write({
                    'check_in': rec.pre_check_in if rec.pre_check_in else False,
                    'check_out': rec.pre_check_out if rec.pre_check_out else False,
                })
                rec.state = 'draft'

    @api.onchange('employee_id','att_date')
    def get_previous_checks(self):
        for rec in self:
            if not (rec.employee_id and rec.att_date):
                rec.pre_check_in = False
                rec.pre_check_out = False
                continue

            start_of_day = datetime.combine(self.att_date, datetime.min.time())
            end_of_day = datetime.combine(self.att_date, datetime.max.time())
            search_record = self.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', start_of_day),
                ('check_in', '<=', end_of_day),
            ])
            if search_record:
                rec.pre_check_in = search_record.check_in
                rec.pre_check_out = search_record.check_out
            else:
                rec.pre_check_in = False
                rec.pre_check_out = False




    def open_employee_request(self):
        return {
            'name': _('Attendance'),
            'domain': [('employee_id', '=', self.employee_id.id)],
            'view_type': 'form',
            'res_model': 'hr.attendance',
            'view_id': False,
            'view_mode': 'list,form',
            'type': 'ir.actions.act_window',
        }

    def get_attendance_count(self):
        count = self.env['hr.attendance'].search_count([('employee_id', '=', self.employee_id.id)])
        self.attendance_count = count

    def action_ask_approval(self):
        # if self.emp_check_in:
        #     time = datetime.strptime(str(self.emp_check_in),"%Y-%m-%d %H:%M:%S")
        #     new_time = time - timedelta(hours=5)
        #     self.emp_check_in = new_time
        self.write({'state': 'to_be_approved'})
        # self.activity_update()

    def action_confirm(self):
        self.write({'state': 'approve'})
        # self.activity_update()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Request Approved',
                'type': 'rainbow_man',
            }
        }

    def action_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    def _get_responsible_for_approval(self):
        if self.state == 'to_be_approved' and self.responsible_id:
            return self.responsible_id
        return self.env['res.users']

    # def activity_update(self):
    #     to_clean, to_do = self.env['attendance.adjustment'], self.env['attendance.adjustment']
    #     for plan in self:
    #         if plan.state == 'draft':
    #             to_clean |= plan
    #         elif plan.state == 'to_be_approved':
    #             plan.activity_schedule(
    #                 'sg_attendance_adjustment_request.mail_act_schedule_attendance_adjustment',
    #                 user_id=plan.sudo()._get_responsible_for_approval().id or self.env.user.id)
    #         elif plan.state == 'approve':
    #             to_clean |= plan
    #
    #     if to_clean:
    #         to_clean.activity_unlink(['sg_attendance_adjustment_request.mail_act_schedule_attendance_adjustment'])

    def create_attendance(self):
        search_attendance = self.env['hr.attendance']
        print("here boi")
        start_of_day = datetime.combine(self.att_date, datetime.min.time())
        end_of_day = datetime.combine(self.att_date, datetime.max.time())

        search_record = search_attendance.search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '>=', start_of_day),
            ('check_in', '<=', end_of_day),
        ])

        print('My search record', search_record)
        if search_record:
            print('My write')
            search_record.write({
                'check_in': self.emp_check_in,
                'check_out': self.emp_check_out,

            })
        else:
            print('My create')
            search_record.create({
                'employee_id': self.employee_id.id,
                'check_in': self.emp_check_in,
                'check_out': self.emp_check_out,
            })
        return self.write({'state': 'done'})
