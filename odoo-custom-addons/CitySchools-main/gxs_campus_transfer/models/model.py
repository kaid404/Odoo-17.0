from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)
from datetime import date , datetime
from datetime import timedelta

class ProductConfiguratorSale(models.TransientModel):
    _name = "gxs.campus.transfer"


    student_ids = fields.Many2many(
        'op.student',
        string='Students',
        required=True,

        default=lambda self: self._default_students()
    )

    company_id = fields.Many2one(
        'res.company', string='Campus',
        default=lambda self: self.env.user.company_id)

    def _default_students(self):
        active_ids = self.env.context.get('active_ids')

        print(active_ids)
        return active_ids
        # return self.env['op.student'].search([('active', '=', True)])


    def transfer(self):

        for rec in self.student_ids:
            rec.sudo().user_id.company_ids = rec.user_id.company_ids.ids +self.company_id.ids
            rec.sudo().user_id.company_id = self.company_id.id
            print('>>>>>>>>>>>3')

            rec.sudo().partner_id.company_id = self.company_id.id

            print('>>>>>>>>>1')
            rec.sudo().company_id = self.company_id.id

            print('>>>>>>>>>>2')



