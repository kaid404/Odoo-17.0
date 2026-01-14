from odoo import models,fields,api
from odoo.exceptions import ValidationError

class PromoteStudents(models.TransientModel):
    _name = 'promote.student'
    _description = 'Promote Students'

    class_id = fields.Many2one('op.academic.term', string='Year')
    year_id = fields.Many2one('op.academic.year', string='Next Class')
    section_id = fields.Many2one('class.section', string='Next Section')
    from_class_id = fields.Many2one('op.academic.year', string='Current Class')
    from_section_id = fields.Many2one('class.section', string='Current Section')
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
        course = self.env['op.student.course']
        current_course = self.env['op.course']
        registration = self.env['op.subject.registration']
        for student in self.student_ids:
            # Update student class, year, and section
            student.class_id = self.class_id.id
            student.year_id = self.year_id.id
            student.section_id = self.section_id.id
            new_course = current_course.search([('class_id', '=', self.year_id.id)], limit=1).id
            if not new_course:
                raise ValidationError('No course available for %s '%self.year_id.name)

            # Remove the student from the previous section's student_ids
            if self.from_section_id:
                self.from_section_id.write({
                    'students': [(3, student.id)]
                })

            # Add the student to the new section's student_ids
            if self.section_id:
                self.section_id.write({
                    'students': [(4, student.id)]
                })
            #register
            prev_course = course.search([('academic_years_id','=',self.from_class_id.id)],limit=1)
            prev_course.write({'state':'finished'})
            course.create({
                'student_id':student.id,
                'academic_years_id':self.year_id.id,
                'course_id': new_course,
                'academic_term_id':self.class_id.id,
            })
            registered = registration.create({
                'student_id':student.id,
                'course_id':new_course,
                'class_id':self.year_id.id,
            })

            registered.get_subjects()
            registered.action_submitted()
            registered.action_approve()

