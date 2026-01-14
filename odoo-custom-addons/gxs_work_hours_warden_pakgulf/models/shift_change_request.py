# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, time, timedelta,date


class TodoTask(models.Model):
    _name = 'shift.change.request'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    current_shift = fields.Many2one('resource.calendar',string='Current Shift')
    new_shift = fields.Many2one('resource.calendar',string='New Shift')
    description = fields.Char(string='Description')
    state = fields.Selection([
        ('draft', "Draft"),
        ('to_approve', "To Approve"),
        ('reject', "Reject"),
        ('approve', "Approved"),
         ], string="Status", default='draft')

    check_in = fields.Datetime(string='Check in')
    check_out = fields.Datetime(string='Check out')

    @api.onchange('employee_id')
    def onchange_add_shift(self):
        if self.employee_id:
            for rec in self:
                emp = self.env['hr.employee'].search(
                    [('id', '=', rec.employee_id.id)])
                self.current_shift = emp.resource_calendar_id
    def create_shift(self):
        emp = self.env['hr.employee'].search(
            [('id', '=', self.employee_id.id)])
        emp.write({'resource_calendar_id':self.new_shift.id})
        self.state = 'approve'
    def reject(self):
        self.state = 'reject'
    def to_approve(self):
        self.state = 'to_approve'

