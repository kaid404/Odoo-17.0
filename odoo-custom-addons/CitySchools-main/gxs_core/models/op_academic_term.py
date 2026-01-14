from odoo import models, fields ,api
from odoo.exceptions import ValidationError


class OpAcademicTerm(models.Model):

    _name = 'op.academic.term'
    _description = "Academic Year"

    name = fields.Char('Name', required=True)
    term_start_date = fields.Date('Start Date', required=True)
    term_end_date = fields.Date('End Date', required=True)
    academic_year_id = fields.Many2one(
        'op.academic.year', 'Academic Class', required=False)
    parent_term = fields.Many2one('op.academic.term', 'Parent year')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    current_year = fields.Boolean(string="Current year")

    @api.constrains('parent_id')
    def _check_parent_id_recursion(self):
        old = self.env['op.academic.term'].search([('current_year','=',True),('id','=',self.id)])
        if old:
            raise ValidationError(('You cannot set multiple years as current year'))
