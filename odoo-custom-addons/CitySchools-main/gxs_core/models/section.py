from odoo import models,fields,api

class ClassSection(models.Model):
    _name = 'class.section'
    _description = 'Class Section'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']


    class_id = fields.Many2one('op.academic.year', string='Class', store=True, copy=True)
    year_id = fields.Many2one('op.academic.term', string='Year', store=True, copy=True)
    name = fields.Char('Section Name',store=True)
    faculty = fields.Many2one(
        'op.faculty', 'Faculty', required=False)

    students = fields.Many2many('op.student',string='Students',copy=False,store=True)


    
    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            
            name = name + '-' + rec.class_id.name
            result.append((rec.id, name))
        return result


    @api.constrains('students')
    def get_student_section(self):
        for rec in self:
            for std in rec.students:
                if not std.section_id:
                    std.section_id = rec.id


class OdooCMSStudent(models.Model):
    _inherit = 'op.student'


    @api.constrains('section_id')
    def get_student_section(self):
        for rec in self:
            for sec in rec.section_id:
                sec.students = sec.students.ids + rec.ids
