from odoo import models, fields


class OpExamType(models.Model):
    _name = "op.exam.type"
    _description = "Exam Type"

    name = fields.Char('Name', size=256, required=True)
    code = fields.Char('Code', size=16, required=True)

    _sql_constraints = [
        ('unique_exam_type_code',
         'unique(code)', 'Code should be unique per exam type!')]
