from email.policy import default

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class JobRequisition(models.Model):
    _name = 'job.requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Job Requisition Form'
    _rec_name = 'sequence'

    sequence = fields.Char(string='Sequence', default=lambda self: self._get_default_ref(),
                           help="Gives the sequence order when displaying a list of job requisitions")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submit', 'Submit'),
        ], default='draft', string='State', store=True, tracking=True, copy=False)
    requested_by = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        tracking=True
    )

    email_id = fields.Char(
        string="Email",
        compute='_compute_email_id',
        store=True
    )
    team_name1 = fields.Many2one(
        'x_team',
        string="Team Name",
        compute='_compute_email_id',
        store=True
    )

    @api.depends('requested_by')
    def _compute_email_id(self):
        for rec in self:
            employee = self.env['hr.employee'].search(
                [('user_id', '=', rec.requested_by.id)],
                limit=1
            )
            rec.email_id = employee.work_email if employee else False
            rec.team_name1 = employee.x_studio_team if employee else False
    # email_id = fields.Char(string="Email")
    team_name = fields.Char(string="Team Name")
    hiring_position = fields.Many2one('hr.job', string="Hiring Position")
    number_of_positions = fields.Char(string="Number Of Position")
    job_type = fields.Selection([
        ('permanent', "Permanent"),
        ('internship', "Internship"),
        ('traineeship', "Traineeship"),
        ('contractual', "Contractual"),
        ('other', "Other"),
    ], string='Job Type', default=False)

    justification = fields.Selection([
        ('termination', "Replacement due to termination"),
        ('resignation', "Replacement due to resignation"),
        ('replacement', "Replacement due to internal transfer within Game District"),
        ('addition', "Addition due to increased workload"),
    ], string='Position Requirement Justification', default=False)
    # justification = fields.Char(string="Justification")
    replacement = fields.Html(string="Replacement")
    reason_for_relieving = fields.Many2many('reason.relieving', string="Reason For Leaving")
    other_reason = fields.Char('Other Reason')
    show_other_reason = fields.Boolean(string="Show Other Reason",  compute="_compute_show_other_reason",store=True)

    job_specification = fields.Many2many('job.specifications', string="Role Requirements")
    other_job = fields.Char(string='Other')
    show_other_job = fields.Boolean(string="Show Other Job",  compute="_compute_show_other_job",store=True)

    related_experience = fields.Selection([
        ('entry_lvl', "Entry Level (Fresh-1 Year)"),
        ('junior_lvl', "Junior Career Level 1-2 Years"),
        ('mid_lvl', "Mid Career Level 2-4 Years"),
        ('experience_lvl', "Experienced 5-10 Years"),
        ('senior_lvl', "Senior Executive Professional (10-20 Years)"),
    ], string='Related Experience', default='entry_lvl')
    proposed_salary = fields.Selection([
        ('unpaid_to_thirty', "Unpaid-30000"),
        ('thirty_to_one_lac', "30000-100000"),
        ('one_to_two_lac', "100000-200000"),
        ('two_to_three_lac', "200000-300000"),
        ('three_to_five_lac', "300000-500000"),
        ('other', "Other"),
    ], string='Proposed Salary', default=False)
    other_salary_check = fields.Boolean(string="Proposed Salary")
    other_salary = fields.Float(string="Proposed Salary")

    # is_test_conducted = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Is Test Conducted')
    test_to_be_conducted = fields.Selection([('previously_designed_test', 'Previously Designed Test'),
                                             ('new_test_to_be_designed_specific_to_the_team_need',
                                              'New Test To Be Designed Specific To The Team"s Need'),('yes','Yes'),('no','No')],
                                            string='New Test To Be Designed Specific To The Team Need')

    any_special_skills = fields.Html(string="Any Special Skills")
    date = fields.Date(string="Date",default=date.today())

    skill = fields.Char(string="Any Special Skill")
    budget_information= fields.Many2many('budget.information', string="Budget Information")
    other_budget = fields.Char(string='Other Budget')
    show_other_budget = fields.Boolean(string="Show Other Approval")
    approval_ceo= fields.Many2many('approval.ceo', string="Approval Ceo")
    other_approval = fields.Char(string='Other Approval')
    show_other_approval = fields.Boolean(string="Show Other Approval")

    @api.depends('reason_for_relieving')
    def _compute_show_other_reason(self):
        for rec in self:
            rec.show_other_reason = any(
                reason.name == 'Other'
                for reason in rec.reason_for_relieving
            )

    @api.depends('job_specification')
    def _compute_show_other_job(self):
        for rec in self:
            rec.show_other_job = any(
                job.name == 'Other'
                for job in rec.job_specification
            )

    @api.onchange('proposed_salary')
    def set_other_Salary(self):
        for rec in self:
            if rec.proposed_salary == 'other':
                rec.other_salary_check = True
            else:
                rec.other_salary_check = False



    @api.onchange('budget_information')
    def _compute_show_other_budget(self):
        other_option = self.env.ref('job_requisition.budget_other', raise_if_not_found=False)
        for rec in self:
            rec.show_other_budget = other_option and other_option.id in rec.budget_information.ids

    @api.onchange('approval_ceo')
    def _compute_show_other_approval(self):
        other_option = self.env.ref('job_requisition.approval_ceo_other', raise_if_not_found=False)
        for rec in self:
            rec.show_other_approval = other_option and other_option.id in rec.approval_ceo.ids




    @api.model
    def _get_default_ref(self):
        # You might want to use a sequence for the ref field as well
        return self.env['ir.sequence'].next_by_code('job.requisition') or 'New'

    def action_submit(self):
        self.state = 'submit'