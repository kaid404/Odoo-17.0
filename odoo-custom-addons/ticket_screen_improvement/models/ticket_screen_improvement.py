from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TicketScreenImprovement(models.Model):
    _inherit = 'helpdesk.ticket'

    pro_id = fields.Many2one('project.project', string="Project")
    tasks_tagging = fields.Many2one('project.task', string="Tasks", domain="[('project_id', '=', pro_id)]")
    multi_assignees = fields.Many2many('res.users', string="Multi Assignees")
    functional_team = fields.Many2one('helpdesk.team', string="Functional Team")
    #
    # dev_team_status = fields.Selection([('completed', 'Completed'), ('in_progress', 'InProgress')],
    #                                    string="Dev Team")

    video_link = fields.Char(string="Video Link")

    description_locked = fields.Boolean(string="Description Locked", default=False)


    def notifying_users_for_tickets(self):
        three_days_ago = fields.Datetime.now() - timedelta(days=3)
        old_tickets = self.search([
            ('create_date', '<=', three_days_ago),
        ])

        for ticket in old_tickets:
            if ticket.user_id:
                ticket.message_post(
                    body="Sir! Your ticket is still pending...",
                    partner_ids=[ticket.user_id.partner_id.id]
                )

            if ticket.multi_assignees:
                for user in ticket.multi_assignees:
                    if user != ticket.user_id:
                        ticket.message_post(
                            body="Sir! Your ticket is still pending...",
                            partner_ids=[user.partner_id.id]
                        )

    @api.model
    def create(self, vals):
        if vals.get('description'):
            vals['description_locked'] = True
        return super(TicketScreenImprovement, self).create(vals)

    def write(self, vals):
        for record in self:
            if record.description_locked and 'description' in vals:
                raise ValidationError("Description can't be edited once it is submitted")
        return super(TicketScreenImprovement, self).write(vals)
