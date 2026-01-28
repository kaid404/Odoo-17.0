from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ParametersMarksWizard(models.TransientModel):
    _name = 'parameters.marks'
    _description = 'Parameters Marks Wizard'

    training_program_id = fields.Many2one('pixls.training.program', string="Training Program")
    parameters_line_id = fields.Many2one('parameters.line', string="Parameter")
    parameters_id = fields.Many2one('assignment.parameters', string="Parameter")
    jury_member_id = fields.Many2one('hr.employee',store=True, string="Jury Member")
    line_ids = fields.One2many('parameters.marks.line', 'parameters_marks_id', string="Parameters Marks Lines")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        user = self.env.user

        employee = user.partner_id.employee_ids[:1]
        if employee:
            res['jury_member_id'] = employee.id

        if active_id:
            parameters_line = self.env['parameters.line'].browse(active_id)
            # program = self.env['pixls.training.program'].browse(active_id)
            program = parameters_line.training_program_id
            res['training_program_id'] = program.id
            res['parameters_line_id'] = parameters_line.id
            res['parameters_id'] = parameters_line.parameters_id.id
            res['line_ids'] = [(0, 0, {'student_id': s.student_id.id}) for s in program.students]
        return res

    def action_confirm(self):
        for rec in self:
            program = rec.training_program_id
            jury_members = program.jury_members_lines_id
            for line in rec.line_ids:
                existing = self.env['jury.members.marks'].search([
                    ('training_program_id', '=', program.id),
                    ('jury_member_id', '=', rec.jury_member_id.id),
                    ('parameters_id', '=', rec.parameters_id.id),
                    ('student_id', '=', line.student_id.id),
                ], limit=1)

                if existing:
                    existing.write({'marks': line.marks})
                else:
                    self.env['jury.members.marks'].create({
                        'training_program_id': program.id,
                        'parameters_line_id': rec.parameters_line_id.id,
                        'parameters_id': rec.parameters_id.id,
                        'student_id': line.student_id.id,
                        'jury_member_id': rec.jury_member_id.id,
                        'marks': line.marks,
                        'remarks': line.remarks,
                    })
            for jury in jury_members:
                jury.total_jury_marks()
            for st in program.students:
                st.total_jury_marks()

        return {'type': 'ir.actions.act_window_close'}


class ParametersMarksLine(models.TransientModel):
    _name = 'parameters.marks.line'
    _description = 'Parameters Marks Line'

    parameters_marks_id = fields.Many2one('parameters.marks', string="Sheet")
    student_id = fields.Many2one('hr.employee', string="Student")
    marks = fields.Float(string="Marks")
    remarks = fields.Char(string="Remarks")
