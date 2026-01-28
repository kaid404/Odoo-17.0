from odoo import fields, models, api
from odoo.exceptions import ValidationError


class AssignmentData(models.Model):
    _name = "assignment.data"

    name = fields.Char(string='Name')
    weightage = fields.Float(string='Weightage')
    total_marks = fields.Float(string='Total Marks')
    line_ids = fields.One2many('assignment.data.lines', 'assignment_id', string='Name')
    training_program_id = fields.Many2one('pixls.training.program', string='Training Program', ondelete='cascade',required=True)
    program_ids = fields.Many2many('pixls.training.program', string='Training Program', compute='_get_training_program_domain')
    trainer_id = fields.Many2one('hr.employee',string='Trainer',required=True, domain="[('id','in',available_trainers_ids)]")
    available_trainers_ids = fields.Many2many('hr.employee',string='Available Trainers',compute='_compute_available_trainers',store=False)

    def _get_training_program_domain(self):
        admin_group = self.env.ref(
            'pixls_training_program.group_training_admin',
            raise_if_not_found=False
        )

        for rec in self:
            if admin_group and admin_group in self.env.user.groups_id:
                rec.program_ids = self.env['pixls.training.program'].search([])
            else:
                rec.program_ids = self.env['pixls.training.program'].search([
                    ('trainer', 'in', self.env.user.employee_ids.ids)
                ])

    @api.constrains('trainer_id')
    def _check_trainer_ids(self):
        admin_group = self.env.ref(
            'pixls_training_program.group_training_admin',
            raise_if_not_found=False
        )
        current_employee = self.env.user.employee_ids[:1]

        for rec in self:
            if admin_group and admin_group in self.env.user.groups_id:
                continue

            if rec.trainer_id == current_employee:
                continue

            raise ValidationError(
                "You cannot change the trainer. Only Admins can modify this field."
            )

    @api.depends('training_program_id')
    def _compute_available_trainers(self):
        for rec in self:
            if rec.training_program_id:
                rec.available_trainers_ids = rec.training_program_id.trainer.ids
            else:
                rec.available_trainers_ids = False
    
    @api.constrains('')
    def create_dynamic_field_and_view(self):
        pass

    @api.onchange('training_program_id')
    def create_dynamic_field_and_view(self):
        for rec in self:
            if rec.training_program_id:
                rec.trainer_id = self.env.user.employee_ids[:1].id

class AssignmentDataLines(models.Model):
    _name = "assignment.data.lines"

    assignment_id = fields.Many2one('assignment.data', string='Assignment', ondelete='cascade')
    marks = fields.Float(string='Marks')
    name = fields.Many2one('assignment.goals', string='Name')

    @api.constrains('marks')
    def _check_marks_limit(self):
        for rec in self:
            if rec.assignment_id:
                total_marks = rec.assignment_id.total_marks
                line_count = len(rec.assignment_id.line_ids)

                # if line_count > 0:
                #     allowed_marks = total_marks / line_count
                #
                #     if rec.marks > allowed_marks:
                #         raise ValidationError(
                #             f"Marks cannot exceed {allowed_marks:.2f} because total marks "
                #             f"{total_marks} are divided among {line_count} goals."
                #         )

                total_lines_marks = sum(line.marks for line in rec.assignment_id.line_ids)

                if total_lines_marks > total_marks:
                    raise ValidationError(
                        f"Total marks of all lines ({total_lines_marks}) "
                        f"cannot exceed assignment total marks ({total_marks})."
                    )


class AssignmentGoals(models.Model):
    _name = "assignment.goals"

    name = fields.Char(string='Name')


class AssignmentTrainerResult(models.Model):
    _name = "assignment.trainer.result"
    _description  = "Pixls Training Program Result"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'



    name = fields.Char(string='Name',compute="_get_compute_name")
    trainer = fields.Many2one('hr.employee', string='Trainer',required=True, domain=[('is_pixls_st', '=', False)])
    training_program_id = fields.Many2one('pixls.training.program', string='Training Program',required=True, domain="[('trainer','ilike',trainer)]")
    student_lines_id = fields.One2many('assignment.training.student.result.line', 'assignement_result_id', string='Result Lines')

    @api.constrains('trainer')
    def _check_trainer_ids(self):
        admin_group = self.env.ref(
            'pixls_training_program.group_training_admin',
            raise_if_not_found=False
        )
        current_employee = self.env.user.employee_ids[:1]

        for rec in self:
            if admin_group and admin_group in self.env.user.groups_id:
                continue

            if rec.trainer == current_employee:
                continue

            raise ValidationError(
                "You cannot change the trainer. Only Admins can modify this field."
            )

    @api.depends('training_program_id', 'trainer')
    def _get_compute_name(self):
        for rec in self:
            name_parts = []
            
            if rec.training_program_id:
                name_parts.append(rec.training_program_id.name)
            if rec.trainer:
                name_parts.append(rec.trainer.name)
            rec.name = " - ".join(name_parts)
            
    @api.onchange('trainer', 'training_program_id')
    def _get_student_lines(self):
        for rec in self:
            rec.student_lines_id = [(5, 0, 0)]
            if rec.training_program_id:
                line_vals = []
                for student in rec.training_program_id.students:
                    for assignment in self.env['assignment.data'].search([('trainer_id','=',rec.trainer.id),('training_program_id','=',rec.training_program_id.id)],order="id desc"):
                        subline_vals = []
                        for line in assignment.line_ids:
                            subline_vals.append((0, 0, {
                                'goal_id': line.name.id,
                                'total_marks': line.marks,
                            }))

                        line_vals.append((0, 0, {
                            'student_id': student.student_id.id,
                            'training_program_id': rec.training_program_id.id,
                            'assignement_id': assignment.id,
                            'assignement_result_id': rec.id,
                            'subline_ids': subline_vals,
                        }))
                
                rec.student_lines_id = line_vals


class AssignmentTrainerResultLines(models.Model):
    _name = "assignment.training.student.result.line"
    _description = "Pixls Training Program Student Result"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'assignement_id desc'
    
    training_program_id = fields.Many2one('training.program', string='Training Program')
    assignement_result_id = fields.Many2one('assignment.trainer.result', string='Assignment Result',required=True)
    assignement_id = fields.Many2one('assignment.data', string='Assignment',required=True)
    student_id = fields.Many2one('hr.employee', string='Student', required=True, domain=[('is_pixls_st', '=', True)])
    remarks = fields.Char(string="Overall Remarks")
    total = fields.Float(string='Total', store=True, compute='compute_total_marks')
    obt_total = fields.Float(string='Obtained Total', store=True, compute='compute_obt_marks')
    warning_check = fields.Boolean(string='Warning')
    warning_reason = fields.Char(string='Warning Reason')
    warning_date = fields.Date(string='Warning Date')
    subline_ids = fields.One2many('assignment.training.student.result.subline', 'result_line_id', string="Goal Marks")

    @api.depends('subline_ids', 'subline_ids.obt_marks')
    def compute_obt_marks(self):
        for rec in self:
            rec.obt_total = sum(line.obt_marks or 0 for line in rec.subline_ids)

    @api.depends('subline_ids', 'subline_ids.total_marks')
    def compute_total_marks(self):
        for rec in self:
            rec.total = sum(line.total_marks or 0 for line in rec.subline_ids)


class AssignmentTrainerResultSubLines(models.Model):
    _name = "assignment.training.student.result.subline"

    result_line_id = fields.Many2one('assignment.training.student.result.line', required=True, ondelete='cascade')
    goal_id = fields.Many2one('assignment.goals',string='Goal', required=True)
    total_marks = fields.Float(string='Total Marks', compute='_compute_total_marks', store=True)
    obt_marks = fields.Float(string='Obt. Marks', store=True)

    @api.depends('goal_id', 'result_line_id.assignement_id')
    def _compute_total_marks(self):
        for rec in self:
            rec.total_marks = 0
            if rec.goal_id and rec.result_line_id.assignement_id:
                line = self.env['assignment.data.lines'].search([
                    ('assignment_id', '=', rec.result_line_id.assignement_id.id),
                    ('name', '=', rec.goal_id.name)
                ], limit=1)

                rec.total_marks = line.marks if line else 0


    @api.onchange('obt_marks')
    def _check_obt_marks(self):
        for rec in self:
            if rec.obt_marks > rec.total_marks:
                raise ValidationError(f"Obtained marks ({rec.obt_marks}) cannot be greater than total marks ({rec.total_marks}).")





