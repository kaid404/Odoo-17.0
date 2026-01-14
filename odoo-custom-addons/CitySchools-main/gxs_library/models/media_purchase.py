from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpMediaPurchase(models.Model):
    _name = "op.media.purchase"
    _inherit = "mail.thread"
    _description = "Media Purchase Request"

    name = fields.Char('Title', size=128, required=True)
    author = fields.Char(
        'Author(s)', size=256, required=True, tracking=True)
    edition = fields.Char('Edition')
    publisher = fields.Char('Publisher(s)', size=256)
    course_ids = fields.Many2one(
        'op.course', 'Course', required=True, tracking=True)
    subject_ids = fields.Many2one(
        'op.subject', 'Subject', required=True, tracking=True)
    requested_id = fields.Many2one(
        'res.partner', 'Requested By',
        default=lambda self: self.env.user.partner_id.id)
    state = fields.Selection(
        [('draft', 'Draft'), ('request', 'Requested'),
         ('reject', 'Rejected'), ('accept', 'Accepted')],
        'State', readonly=True, default='draft', tracking=True)
    media_type_id = fields.Many2one('op.media.type', 'Media Type')
    active = fields.Boolean(default=True)

    def act_requested(self):
        self.state = 'request'

    def act_accept(self):
        self.state = 'accept'

    def act_reject(self):
        self.state = 'reject'

    @api.model_create_multi
    def create(self, vals):
        if self.env.user.child_ids:
            raise ValidationError(_('Invalid Action!\n Parent can not create \
            Media Purchase Requests!'))
        return super(OpMediaPurchase, self).create(vals)

    def write(self, vals):
        if self.env.user.child_ids:
            raise ValidationError(_('Invalid Action!\n Parent can not edit \
            Media Purchase Requests!'))
        return super(OpMediaPurchase, self).write(vals)
