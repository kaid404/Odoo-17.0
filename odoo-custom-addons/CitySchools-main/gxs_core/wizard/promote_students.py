from odoo import models,fields,api

class PromoteStudents(models.TransientModel):
    _name = 'promote.student'
    _description = 'Promote Students'

    class_id = fields.Many2one('op.academic.term', string='Academic Year')
    year_id = fields.Many2one('op.academic.year', string='Academic Class')
    section_id = fields.Many2one('class.section', string='Section')
    from_class_id = fields.Many2one('op.academic.term', string='Academic Year')
    from_section_id = fields.Many2one('class.section', string='Section')
    student_ids = fields.Many2many('op.student',string = 'Student')

    @api.onchange('from_section_id')
    def get_students(self):
        if self.from_section_id:
            # Search for students in the selected section
            students = self.env['op.student'].search([('section_id', '=', self.from_section_id.id)])
            self.student_ids = students
        else:
            # Clear the students list if no section is selected
            self.student_ids = [(5, 0, 0)]


    def promote_students(self):
        for rec in self:
            pass
