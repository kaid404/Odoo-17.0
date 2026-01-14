from odoo import models, fields, api

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def action_send_employment_form(self):
        self.ensure_one()
        template = self.env.ref('portal_employment_application.email_template_employment_form')
        template.send_mail(self.id, force_send=True)
        return True
