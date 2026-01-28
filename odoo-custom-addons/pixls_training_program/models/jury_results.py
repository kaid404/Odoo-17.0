from odoo import fields, models, api
from odoo.exceptions import ValidationError

class JuryTrainerResult(models.Model):
    _name = "jury.trainer.result"
    _description  = "Jury Trainer Results"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    training_program_id = fields.Many2one('pixls.training.program', string='Training Program',required=True)
    jury = fields.Many2one('hr.employee', string='Jury',required=True, domain=[('is_pixls_st', '=', False)])
    student_lines_id = fields.One2many('jury.trainer.result.line', 'jury_result_id', string='Student Lines')

    @api.onchange('training_program_id', 'jury')
    def _onchange_program_and_jury(self):
        self.student_lines_id = [(5, 0, 0)]
        if not self.training_program_id or not self.jury:
            return
        if self.jury.id not in self.training_program_id.jury_members_lines_id.mapped('jury_member_id').ids:
            raise ValidationError('This jury is not assigned to the selected training program.')
        lines = []
        for student in self.training_program_id.students:
            lines.append(
                (0, 0, {
                    'student_id': student.student_id.id
                })
            )
        self.student_lines_id = lines


class JuryTrainerResultLines(models.Model):
    _name = "jury.trainer.result.line"
    _description = "Jury Trainer Results"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    jury_result_id = fields.Many2one('jury.trainer.result', string='Assignment Result',required=True)
    student_id = fields.Many2one('hr.employee', string='Student', required=True, domain=[('is_pixls_st', '=', True)])
    remarks = fields.Char(string="Overall Remarks")
    trainer_remarks = fields.Char(string="Trainer Remarks")
    assignment_total = fields.Float(string='Assignment Total', store=True, compute='_compute_total')
    subline_ids = fields.One2many('jury.trainer.result.subline', 'jury_line_id', string="Goal Marks")

    total = fields.Float(string='Total', store=True, compute='compute_total_marks')
    obt_total = fields.Float(string='Obtained Total', store=True, compute='compute_obt_marks')

    @api.depends('subline_ids', 'subline_ids.obt_marks')
    def compute_obt_marks(self):
        for rec in self:
            rec.obt_total = sum(line.obt_marks or 0 for line in rec.subline_ids)

    @api.depends('subline_ids', 'subline_ids.total_marks')
    def compute_total_marks(self):
        for rec in self:
            rec.total = sum(line.total_marks or 0 for line in rec.subline_ids)


    @api.depends('student_id', 'jury_result_id.training_program_id')
    def _compute_total(self):
        for rec in self:
            if not rec.student_id or not rec.jury_result_id.training_program_id:
                rec.assignment_total = 0
                continue

            assignment_lines = self.env['assignment.training.student.result.line'].search([
                ('student_id', '=', rec.student_id.id),
                ('assignement_result_id.training_program_id', '=', rec.jury_result_id.training_program_id.id)
            ])
            rec.assignment_total = sum(line.obt_total for line in assignment_lines)

            rec.subline_ids = [(5, 0, 0)]

            if rec.jury_result_id.training_program_id:
                line_vals = []
                parameters = self.env['assignment.parameters'].search(
                    [('training_program_id', '=', rec.jury_result_id.training_program_id.id)])

                for pr in parameters:
                    line_vals.append((0, 0, {
                        'parameter_id': pr.id,
                        'total_marks': pr.total,
                    }))

                rec.subline_ids = line_vals

class JuryTrainerResultSubLines(models.Model):
    _name = "jury.trainer.result.subline"

    jury_line_id = fields.Many2one('jury.trainer.result.line', required=True, ondelete='cascade')
    parameter_id = fields.Many2one('assignment.parameters',string='Parameter', required=True)
    total_marks = fields.Float(string="Total", readonly=True)
    obt_marks = fields.Float(string="Obtained")
    remarks = fields.Char(string="Remarks")

    @api.onchange('obt_marks')
    def _check_obt_marks(self):
        for rec in self:
            if rec.obt_marks > rec.total_marks:
                raise ValidationError(f"Obtained marks ({rec.obt_marks}) cannot be greater than total marks ({rec.total_marks}).")




