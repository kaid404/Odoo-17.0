from email.policy import default

from odoo import models, fields, api
from datetime import date


class StudentFeeUpdation(models.Model):
    _name = 'student.fee.update'
    _description = 'Student Fee Update'

    student_id = fields.Many2one('op.student', string='Student', required=True)
    gr_number = fields.Char(related='student_id.gr_no', string='Registration Number')
    previous_fee = fields.Float(string='Previous Fee', readonly='True', store=True)
    new_fee = fields.Float(string='Increment Fee', required=True)
    current_date = fields.Date(string='Current Date', required=True, default=fields.Date.today)
    discount = fields.Float(string='Total Discount')
    total_fee = fields.Float(string='Total Fee')

    # @api.model
    # def create(self, vals):
    #     record = super(StudentFeeUpdation, self).create(vals)
    #
    #     record.compute_previous_fee()
    #
    #     if record.new_fee:
    #         record.student_id.write({'amount_fee': record.new_fee + record.student_id.amount_fee})
    #
    #     return record

    # @api.onchange('student_id', 'new_fee')
    # def compute_previous_fee(self):
    #     for record in self:
    #         if record.student_id:
    #             if not record.student_id.id_old_student:
    #                 fee_structures = self.env['fee.structure'].search([
    #                     ('classes', '=', record.student_id.year_id.id),
    #                     ('date_start', '<=', record.current_date),
    #                     ('date_end', '>=', record.current_date),
    #                     ('company_id', '=', record.student_id.company_id.id)
    #                 ], limit=1)
    #
    #                 fee_structure = self.env['fee.details'].search([
    #                     ('structure_id', '=', fee_structures.id),
    #                     ('product_id.name', '=', 'Tuition Fee'),
    #                 ], limit=1)
    #
    #                 if fee_structure:
    #                     record.previous_fee = fee_structure.amount
    #                     record.student_id.id_old_student = True
    #
    #
    #             else:
    #                 record.previous_fee = record.student_id.amount_fee
    #
    # def write(self, vals):
    #     if 'new_fee' in vals or 'student_id' in vals:
    #         self.compute_previous_fee()
    #
    #         if 'new_fee' in vals:
    #             for record in self:
    #                 if vals.get('new_fee'):
    #                     record.student_id.write({'amount_fee': vals.get('new_fee')})
    #     return super(StudentFeeUpdation, self).write(vals)
    #
    # @api.depends('student_id')
    # def _compute_is_saved(self):
    #     for record in self:
    #         record.is_saved = bool(record.id)


class IncrementFee(models.Model):
    _inherit = 'op.student'

    increment_category = fields.Many2one('op.categoryy', string='Fee Category', ondelete="set null")



class CategoryField(models.Model):
    _inherit = 'op.admission'

    increment_category = fields.Many2one('op.categoryy', string='Fee Category', required=True)
    # std_fee = fields.Float(string='Admission Fee')

    def write(self, vals):
        res = super(CategoryField, self).write(vals)
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if record.student_id:
                    record.student_id.increment_category = record.increment_category

        # if 'std_fee':
        #     for record in self:
        #         if record.student_id:
        #             record.student_id.amount_fee = record.std_fee

        return res



