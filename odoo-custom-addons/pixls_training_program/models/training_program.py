from operator import truediv

from odoo import fields, models, api
import logging

logger = logging.getLogger(__name__)


class AssignmentTrainingProgram(models.Model):
    _name = "pixls.training.program"
    _description  = "Pixls Training Program"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'start_date desc'

    name = fields.Char(string="Name", compute="_get_compute_name")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    training_program = fields.Many2one('training.program', string='Training Program')
    trainer = fields.Many2many('hr.employee', string='Trainers', domain=[('is_pixls_st', '=', False)])
    students = fields.One2many('pixls.training.student.line', 'training_program_id', string='Students')
    assignments = fields.One2many('pixls.training.assignment.line', 'training_program_id', string='Students')
    parameters_lines_id = fields.One2many('parameters.line', 'training_program_id', string='Parameters Lines')
    jury_members_lines_id = fields.One2many('jury.members.line', 'training_program_id', string='Jury Members Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In-progress'),
        ('done', 'Done'),
    ], string='State', default='draft')


    @api.depends('start_date','end_date','training_program')
    def _get_compute_name(self):
        for rec in self:
            name_parts = []

            if rec.training_program:
                name_parts.append(rec.training_program.name)

            if rec.start_date and rec.end_date:
                start = rec.start_date.strftime('%b %y')
                end = rec.end_date.strftime('%b %y')
                name_parts.append(f"{start} - {end}")

            rec.name = " ".join(name_parts)
            

    def inprogress_button(self):
        self.state = 'in_progress'

    def done_button(self):
        self.state = 'done'

    def reset_to_draft_button(self):
        self.state = 'draft'


class TrainingStudentLine(models.Model):
    _name = 'pixls.training.student.line'
    _description = 'Training Student Line'

    training_program_id = fields.Many2one('pixls.training.program', string='Training Program', ondelete='cascade')
    student_id = fields.Many2one('hr.employee', string='Student', required=True, domain=[('is_pixls_st', '=', True)])
    remarks = fields.Char(string="Overall Remarks")
    total = fields.Float(string='Total', store=True, readonly=True)
    jury_total = fields.Float(string='Jury Total', store=True, readonly=True)

    def total_weight_percentage(self):
        for rec in self:
            rec.total = 0
            assignment_lines = self.env['assignment.details.line'].search([
                ('assignment_details_id.training_program_id', '=', rec.training_program_id.id),
                ('student_id', '=', rec.student_id.id),
            ])

            total_weight = 0
            for line in assignment_lines:
                if line.total_marks > 0:
                    percentage = (line.marks / line.total_marks) * 100
                    weighted = (percentage * line.assignment_details_id.weightage) / 100
                    total_weight += weighted

            rec.total = total_weight

    def total_jury_marks(self):
        for rec in self:
            rec.jury_total = 0
            jury_members_marks = sum(self.env['jury.members.marks'].search([
                ('training_program_id', '=', rec.training_program_id.id),
                ('student_id', '=', rec.student_id.id),
            ]).mapped('marks'))
            logger.info("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
            logger.info("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
            logger.info("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
            logger.info("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
            logger.info(rec.student_id)
            logger.info(jury_members_marks)

            rec.jury_total = jury_members_marks


class TrainingAssignmentLine(models.Model):
    _name = 'pixls.training.assignment.line'
    _description = 'Training Assignment Line'

    training_program_id = fields.Many2one('pixls.training.program', string='Training Program', ondelete='cascade')
    week = fields.Selection([('week_1', 'Week 1'), ('week_2', 'Week 2')], string='Week', required=True, default=False)
    assignment_id = fields.Many2one('assignment.data', string='Assignment', required=True)

    def action_add_marks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignment Sheet',
            'res_model': 'assignment.sheet',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    def action_assignment_details(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignment Details',
            'res_model': 'assignment.details',
            'view_mode': 'list,form',
            'domain': [('training_assignment_line_id', '=', self.id)],
        }


class JuryMembersLine(models.Model):
    _name = 'jury.members.line'
    _description = 'Jury Members Line'

    training_program_id = fields.Many2one('pixls.training.program', string='Training Program', ondelete='cascade')
    jury_member_id = fields.Many2one('hr.employee', string='Jury Member', domain=[('is_pixls_st', '=', False)])
    total = fields.Float(string='Total', store=True, readonly=True)

    def total_jury_marks(self):
        for rec in self:
            rec.total = 0
            jury_members_marks = sum(self.env['jury.members.marks'].search([
                ('training_program_id', '=', rec.training_program_id.id),
                ('jury_member_id', '=', rec.jury_member_id.id),
            ]).mapped('marks'))

            rec.total = jury_members_marks


class ParametersLine(models.Model):
    _name = 'parameters.line'
    _description = 'Parameters Line'
    _rec_name = 'parameters_id'

    training_program_id = fields.Many2one('pixls.training.program', string='Training Program', ondelete='cascade')
    parameters_id = fields.Many2one('assignment.parameters', string='Parameter')

    def action_add_parameters(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parameters Marks',
            'res_model': 'parameters.marks',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    def action_view_jury_members_marks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Jury Members Marks',
            'res_model': 'jury.members.marks',
            'view_mode': 'list,form',
            'domain': [('training_program_id', '=', self.training_program_id.id)],
        }


class TrainingProgram(models.Model):
    _name = "training.program"

    name = fields.Char(string='Name', required=True)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    training_program_id = fields.Many2one('pixls.training.program', string='Training Program', ondelete='cascade')
    is_pixls_st = fields.Boolean(string='Is Pixls Student')
