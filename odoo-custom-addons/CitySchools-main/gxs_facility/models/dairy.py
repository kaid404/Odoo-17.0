from odoo import models, fields


class OpSubjectDairy(models.Model):
    _name = "op.subject.dairy"
    faculty_id = fields.Many2one('op.faculty',string="Faculty")
    date = fields.Date(string="Date")
    comment = fields.Char(string="Comment")
    class_id = fields.Many2one('op.academic.year', string='Class', store=True, copy=True)
    subject_id = fields.Many2one('op.subject', 'Subject', required=True)
