from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)


class AssignmentSheetWizard(models.TransientModel):
    _name = 'assignment.sheet'
    _description = 'Assignment Sheet Wizard'

    training_program_id = fields.Many2one('pixls.training.program', string="Training Program")
    training_assignment_line_id = fields.Many2one('pixls.training.assignment.line', string="Training Assignment Lines")
    line_ids = fields.One2many('assignment.sheet.line', 'sheet_id', string="Assignment Sheet Lines")
    goal_ids = fields.Many2many('assignment.goals', string="Goals")
    goal_id = fields.Many2one('assignment.goals', string="Goal")
    week = fields.Selection([('week_1', 'Week 1'), ('week_2', 'Week 2')], store=True, string='Week', required=True)
    assignment_id = fields.Many2one('assignment.data', string='Assignment', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            assignment_line = self.env['pixls.training.assignment.line'].browse(active_id)
            # program = self.env['pixls.training.program'].browse(active_id)
            program = assignment_line.training_program_id
            res['training_program_id'] = program.id
            res['training_assignment_line_id'] = assignment_line.id
            res['line_ids'] = [(0, 0, {'student_id': s.student_id.id}) for s in program.students]
            goal_ids = self.env['assignment.data.lines'].search([
                ('assignment_id', 'in', program.assignments.mapped('assignment_id').ids)
            ]).mapped('name.id')
            res['goal_ids'] = [(6, 0, goal_ids)]
            res['assignment_id'] = assignment_line.assignment_id.id
            res['week'] = assignment_line.week
        return res


    def action_confirm(self):
        for rec in self:
            program = rec.training_program_id

            assignment_details = self.env['assignment.details'].search([
                ('training_program_id', '=', program.id),
                ('training_assignment_line_id', '=', rec.training_assignment_line_id.id),
                ('assignment_id', '=', rec.assignment_id.id),
                ('week', '=', rec.week)
            ], limit=1)
            logger.info(assignment_details)

            if not assignment_details:
                assignment_details = self.env['assignment.details'].create({
                    'training_program_id': program.id,
                    'training_assignment_line_id': rec.training_assignment_line_id.id,
                    'assignment_id': rec.assignment_id.id,
                    'week': rec.week,
                })
            for line in rec.line_ids:
                assignment_data = self.env['assignment.data'].search([
                    ('id', '=', rec.training_assignment_line_id.assignment_id.id),
                ], limit=1)

                assignment_line = self.env['assignment.data.lines'].search([
                    ('assignment_id', '=', rec.training_assignment_line_id.assignment_id.id),
                    ('name', '=', rec.goal_id.id)
                ], limit=1)

                assignment_id = assignment_line.assignment_id.id if assignment_line else False
                total_marks = assignment_line.marks if assignment_line else 0.0

                existing_details_line = self.env['assignment.details.line'].search([
                    ('assignment_details_id', '=', assignment_details.id),
                    ('student_id', '=', line.student_id.id),
                ], limit=1)

                logger.info(existing_details_line)

                if existing_details_line:
                    updated_marks = existing_details_line.marks + line.marks
                    existing_details_line.write({
                        'marks': updated_marks,
                        'total_marks': assignment_data.total_marks,
                        'remarks': line.remarks,
                    })

                else:
                    self.env['assignment.details.line'].create({
                        'assignment_details_id': assignment_details.id,
                        'student_id': line.student_id.id,
                        'marks': line.marks,
                        'remarks': line.remarks,
                        'total_marks': assignment_data.total_marks,
                    })
                    assignment_details.write({
                        'total_marks': assignment_data.total_marks
                    })

                existing = self.env['assignment.lines'].search([
                    ('assignment', '=', assignment_id),
                    ('student_id', '=', line.student_id.id),
                    ('goals', '=', rec.goal_id.id),
                    ('week', '=', rec.week)
                ], limit=1)

                if existing:
                    existing.write({'obtained_marks': line.marks})
                else:
                    self.env['assignment.lines'].create({
                        'assignment': assignment_id,
                        'goals': rec.goal_id.id,
                        'week': rec.week,
                        'student_id': line.student_id.id,
                        'obtained_marks': line.marks,
                        'total_marks': total_marks,
                        'remarks': line.remarks,
                    })

        return {'type': 'ir.actions.act_window_close'}


class AssignmentSheetLine(models.TransientModel):
    _name = 'assignment.sheet.line'
    _description = 'Assignment Sheet Line'

    sheet_id = fields.Many2one('assignment.sheet', string="Sheet")
    student_id = fields.Many2one('hr.employee', string="Student")
    marks = fields.Float(string="Marks")
    remarks = fields.Char(string="Remarks")
