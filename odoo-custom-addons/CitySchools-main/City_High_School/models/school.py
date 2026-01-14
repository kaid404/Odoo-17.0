from odoo import api, fields, models, _

class OpAdmission(models.Model):
    _inherit = "op.admission"
    _description = "Op Admission"

    father_name = fields.Char(string="Father Name")
    father_occupation = fields.Char(string="Father Occupation")
    father_education = fields.Char(string="Father Education")
    mother_education = fields.Char(string="Mother Education")
    # phone = fields.Char(string="Phone")
    # mobile = fields.Char(string="Mobile")
    
class OdooCMSStudentTag(models.Model):
    _inherit = 'op.student.tag'
    _description = 'Student Tag'
    
   
    display_name = fields.Char(compute='_compute_display_name', store=False)
    
    @api.depends('name', 'amount')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} - {record.amount}" if record.amount else record.name