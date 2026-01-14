from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    child_move_ids = fields.Many2many(string="Installments",
        comodel_name='account.move',
        relation='child_move_ids_rel',
        column1='child_move_ids_move_id',
        column2='2child_move_ids_move_id',store=True)
    installment_no = fields.Integer(string="Installment No.",default=1)

    def open_child_move_ids(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('id', 'in', self.child_move_ids.ids)]
        return action


