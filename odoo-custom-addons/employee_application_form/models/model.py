from odoo import models, fields, api


class GlobalCompanyField(models.Model):
    _name = 'employment.form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    applicant_id = fields.Many2one('hr.applicant', string="Applicant")


    position_applied = fields.Many2one('hr.job', string='Position Applied', required=True)
    date = fields.Date(string='Date', required=True)
    expected_salary = fields.Float(string='Expected Salary', required=True)
    gross_salary = fields.Float(string='Gross Salary', required=True)


    name = fields.Char(string='Name', required=True)
    date_of_birth = fields.Date(string='Date of birth', required=True)
    mobile_no = fields.Char(string='Mobile #', required=True)
    marital_status = fields.Selection([('single','Single'),('married','Married'),('widower','Widower'),('divorced','Divorced')],string='Marital Status', required=True)
    current_address = fields.Char(string='Current Address', required=True)
    cnic_number = fields.Char(string='Cnic Number', required=True)
    email_id = fields.Char(string='Email Id', required=True)
    qualification_recent = fields.Char(string='Qualification (Recent)', required=True)
    institute_name = fields.Char(string='Institute Name', required=True)
    current_company = fields.Char(string='Current Company', required=True)
    current_job =fields.Char(string='Current Job', required=True)
    total_work_experience = fields.Char(string='Total Work Experience', required=True)
    father_occupation = fields.Char(string='Father Occupation', required=True)
    relatives_employed = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Relatives Employed", required=True)

    previously_employed = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Previously Employed", required=True)


    info_source = fields.Selection([
        ('employee', 'This Company Employee'),
        ('advertisement', 'Advertisement'),
        ('other', 'Other')
    ], string="How did you get job info?", required=True)


    name_1 = fields.Char(string="Name of Employee", required=True)
    relationship_1 = fields.Char(string="Relationship", required=True)
    position_held_1 = fields.Char(string="Position Held", required=True)

    name_2 = fields.Char(string="Name of Employee")
    relationship_2 = fields.Char(string="Relationship")
    position_held_2 = fields.Char(string="Position Held")
    signature = fields.Image(string="Signature", required=True)
    team_name = fields.Char(string='Team Name')
    Interviewer_name = fields.Char(string='Interviewer Name')
    interview_status = fields.Selection([('hire', 'Hire'),('hold' , 'Hold'),('reject','Reject')],string='Interview Status')
    reason = fields.Text(string='Reason')
    visa_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Visa Status')
    additional_uni_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Additional Uni Status')
    work_status_in_pk = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Work Status In Pk')
    name_in_block_letter= fields.Char(string="Name In Block Letter")
    date_signature = fields.Image(string="Date Signature")

class HrApplicant(models.Model):
        _inherit = 'hr.applicant'

        candidates_id = fields.Many2one('employment.form', string='Candidates')
        employment_form_ids = fields.One2many(
            'employment.form', 'applicant_id', string="Employment Applications"
        )

        def action_create_application_form(self):
            return {
                'type': 'ir.actions.act_window',
                'name': 'New Application Form',
                'res_model': 'employment.form',
                'view_mode': 'form',
                'context': {
                    'default_applicant_id': self.id,
                },
                'target': 'current',
            }

        def action_open_applications(self):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Employment Applications',
                'res_model': 'employment.form',
                'view_mode': 'tree,form',
                'domain': [('applicant_id', '=', self.id)],
                'target': 'current',
            }















