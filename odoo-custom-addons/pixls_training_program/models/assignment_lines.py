from odoo import fields, models, api
from datetime import datetime, timedelta

class AssignmentLines(models.Model):
    _name = "assignment.lines"
    _rec_name = 'name'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    assignment = fields.Many2one('assignment.data', string='Assignment')
    goals = fields.Many2one('assignment.goals', string='Goals')
    remarks = fields.Char(string='Remarks')
    student_id = fields.Many2one('hr.employee', string='Student', domain=[('is_pixls_st', '=', True)])
    obtained_marks = fields.Float(string='Obtained')
    total_marks = fields.Float(string='Total Marks')
    week = fields.Selection([('week_1', 'Week 1'), ('week_2', 'Week 2')],store=True, string='Week', required=True)


    @api.depends('student_id','assignment', 'goals')
    def _compute_name(self):
        for rec in self:
            parts = []
            if rec.student_id and rec.student_id.name:
                parts.append(rec.student_id.name)
            if rec.assignment and rec.assignment.name:
                parts.append(rec.assignment.name)
            if rec.goals and rec.goals.name:
                parts.append(rec.goals.name)
            rec.name = ' - '.join(parts) if parts else 'Unnamed'
