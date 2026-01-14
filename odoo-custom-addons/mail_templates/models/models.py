from odoo import models, fields, api
from odoo.exceptions import UserError


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    hr_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=lambda self: [
            ('id', 'in', [
                self.env.ref('mail_templates.email_template_app_shortlisted').id,
                self.env.ref('mail_templates.email_template_hr_recruitment_internship_offer').id,
                self.env.ref('mail_templates.email_template_job_on_hold').id,
                self.env.ref('mail_templates.email_template_hr_recruitment_job_offer').id,
                self.env.ref('mail_templates.email_template_job_rejection').id,
                self.env.ref('mail_templates.email_template_hr_recruitment_required_docs').id,
            ])
        ],
        help="Select one of the predefined HR communication templates."
    )

    def action_open_email_composer(self):
        self.ensure_one()
        if not self.hr_template_id:
            raise UserError("Please select an HR Template first.")

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'view_id': self.env.ref('mail.email_compose_message_wizard_form').id,
            'target': 'new',
            'context': {
                'default_model': 'hr.applicant',
                'default_res_ids': [self.id],
                'default_use_template': True,
                'default_template_id': self.hr_template_id.id,
                'default_composition_mode': 'comment',
                'mark_rfq_as_sent': True,
            },
        }

    def action_mass_send_email(self):
        for rec in self:
            if not rec.hr_template_id:
                raise UserError(f"Applicant {rec.partner_name or rec.name} has no template selected.")
            rec.hr_template_id.send_mail(rec.id, force_send=True)