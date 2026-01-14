from odoo import models, fields, api
from datetime import date


class IncrementCategory(models.Model):
    _name = "op.categoryy"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "increase the fee by category depends on month"

    name = fields.Char(string="Category", required=True, tracking=True)
    increment_fee = fields.Float(string="Increase Fee", required=True, tracking=True)
    fee_add_date = fields.Date(string="Current Date", tracking=True)
    is_computed = fields.Boolean(string="Is Computed", default=False)
    show_recompute = fields.Boolean(string="Show Recompute", compute="_compute_show_recompute", store=True)


    @api.depends('is_computed')
    def _compute_show_recompute(self):
        for rec in self:
            rec.show_recompute = rec.is_computed

    def action_increment(self):
        domain = [('increment_category', '=', self.name)]

        students = self.env['op.student'].search(domain)

        for st in students:
            total_discount = sum(float(tag.amount) for tag in st.tag_ids if tag.amount)

            self.env['student.fee.update'].create({
                'student_id': st.id,
                'previous_fee': st.amount_fee,
                'new_fee': self.increment_fee,
                'current_date': date.today(),
                'discount': total_discount,
                'total_fee': (st.amount_fee + self.increment_fee) - total_discount,
            })
            st.amount_fee += self.increment_fee
            self.fee_add_date = date.today()

        self.is_computed = True

    def action_recompute(self):
        self.is_computed = False


    def compute_amount_fee(self):

        domain = [('id_old_student', '=', False)]

        students = self.env['op.student'].search(domain)

        for st in students:
            fee_structures = self.env['fee.structure'].search([
                ('classes', '=', st.year_id.id),
                ('date_start', '<=', date.today()),
                ('date_end', '>=', date.today()),
                ('company_id', '=', st.company_id.id)
            ], limit=1)

            fee_structure = self.env['fee.details'].search([
                ('structure_id', '=', fee_structures.id),
                ('product_id.name', '=', 'Tuition Fee'),
            ], limit=1)

            if fee_structure:
                st.amount_fee = fee_structure.amount
                st.id_old_student = True
