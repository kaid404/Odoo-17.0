from odoo import models, fields,api
from odoo.osv import expression



class AccountMove(models.Model):
    _inherit = 'account.move'
    student_id = fields.Many2one('op.student',string="Student")
    class_id = fields.Many2one('op.academic.year', string='Academic Class', store=True, copy=True,related='student_id.year_id')
    mobile = fields.Char(strint="Mobile",related='student_id.mobile')
    gr_no = fields.Char(strint="Mobile",related='student_id.gr_no')
    section_id = fields.Many2one('class.section', string='Section',related='student_id.section_id')
    year_id = fields.Many2one('op.academic.term', string='Academic Year', store=True, copy=True,related='student_id.class_id')
    board_reg_number = fields.Char('Board Reg Number',related='student_id.board_reg_number')




class AdmissionRegister(models.Model):
    _inherit = 'op.admission'

    whatsapp_number = fields.Char(string="WhatsApp Number")
    religion_id = fields.Many2one('res.religion', string="Religion")
    nationality = fields.Many2one('res.country',string="Nationality")
    reference_id = fields.Many2one('op.reference', string="Reference")


class Religion(models.Model):
    _name = 'res.religion'
    _description = 'Religion'

    name = fields.Char(string='Religion', required=True)
    description = fields.Text(string='Description')


class OpReference(models.Model):
    _name = 'op.reference'
    _description = 'Reference Master Data'

    name = fields.Char(string='Reference Name', required=True)
    description = fields.Text(string='Description')

class OPStudentInherit(models.Model):
    _inherit = 'op.student'

    sim_number = fields.Char('Sim Number')
    board_reg_number = fields.Char('Board Reg Number')


    # @api.model
    # def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
    #     domain = domain or []
    #     if name:
    #         # Be sure name_search is symetric to display_name
    #         name = name.split(' / ')[-1]
    #         domain = [('name', operator, name)] + domain
    #     return self._search(domain, limit=limit, order=order)

    # @api.model
    # def name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
    #     domain = domain or []
    #     print(name,'[p[poll')
    #     if operator != 'ilike' or (name or '').strip():
    #         name_domain = ['|', ('name', 'ilike', name),('mobile','ilike',name)]
    #         domain = expression.AND([name_domain, domain])
    #     return self._search(domain, limit=limit, order=order)
