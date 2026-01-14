from odoo import models,fields,api

class OdooCMSStudentTag(models.Model):
    _name = 'op.student.tag'
    _description = 'Student Tag'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']


    name = fields.Char(string="Student Tag", required=True, tracking=True)
    code = fields.Char('Tag Code')
    amount = fields.Char('Amount', tracking=True)
    is_admission_discount = fields.Boolean(string="Is Admission Discount")
    is_security_discount = fields.Boolean(string="Is Security Discount")
    # color = fields.Integer(string='Color Index')
    # exclude_fee = fields.Boolean('Exclude Fee', default=False)
    # category_id = fields.Many2one('odoocms.student.tag.category', string='Category')
    # category_code = fields.Char(related='category_id.code', store=True)
    student_ids = fields.Many2many('op.student', string='Group/Tag')
    # group_ids = fields.Many2many('res.groups', 'student_tag_group_rel', 'tag_id', 'group_id', 'Groups')


    @api.constrains('student_ids')
    def get_student_tag(self):
        for rec in self:
            # if rec.tag_ids:
            for std in rec.student_ids:
                if rec.id  not in std.tag_ids.ids:
                    std.tag_ids = std.tag_ids.ids + rec.ids


    @api.model
    def get_student_tag_model(self):
        for rec in self:
            std_list = []
            for std in rec.student_ids:
                if rec.id in std.tag_ids.ids:
                    std_list.append(std.id)
                rec.student_ids = std_list

    # _sql_constraints = [
    #     ('name_uniq', 'unique(name)', "Tag name already exists !"),
    #     ('code_uniq', 'unique(code)', "Tag code already exists !"),
    # ]



class OdooCMSStudent(models.Model):
    _inherit = 'op.student'
    tag_ids = fields.Many2many('op.student.tag',string='Tag(s)')


    @api.constrains('tag_ids')
    def get_student_tag(self):
        for rec in self:
            for tag in rec.tag_ids:
                tag.student_ids = tag.student_ids.ids + rec.ids