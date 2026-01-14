from odoo import models, api, fields
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class EvaluationForm(models.Model):
    _name = 'evaluation.form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Evaluation Form'
    _rec_name = 'candidate_name'

    candidate_name = fields.Many2one('hr.applicant', string="Candidate", store=True, tracking=True)
    initial_interviewer_name = fields.Many2one('res.users', string="Initial Interviewer", store=True, tracking=True)
    final_interviewer_name = fields.Many2one('res.users', string="Final Interviewer", store=True, tracking=True)
    interview_date = fields.Date(string="Interview Date", store=True, tracking=True)
    position = fields.Many2one('hr.job', string="Job Title", store=True, tracking=True)
    template_id = fields.Many2one('evaluation.template', string="Template", store=True, tracking=True,
                                  required=True)
    team_id = fields.Many2one('crm.team', string="Team Name", store=True, tracking=True)

    evaluation_line_ids = fields.One2many('evaluation.form.lines', 'evaluation_id', string="Rating Criteria")
    total_marks = fields.Float(string="Obtained Marks", compute="_compute_marks", store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ], default='draft', string='State', store=True, tracking=True, copy=False)

    scoring = fields.Selection(
        [('not_recommend', 'Not Recommend'), ('maybe_in_future', 'Maybe in Future'), ('recommend', 'Recommend'),
         ('highly_recommend', 'Highly Recommend')], string="Scoring:", readonly=True, store=True,
        compute="_compute_scoring", default=False)
    remarks = fields.Html(string='Remarks & Recommendations')

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_confirm(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.depends('evaluation_line_ids.initial_score')
    def _compute_marks(self):
        score_map = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
        }
        for rec in self:
            total = 0
            for line in rec.evaluation_line_ids:
                score_key = line.final_score or line.initial_score
                if score_key:
                    total += score_map.get(score_key, 0)
            rec.total_marks = total

    @api.depends('total_marks')
    def _compute_scoring(self):
        for rec in self:
            if 20 <= rec.total_marks < 40:
                rec.scoring = 'not_recommend'
            elif 40 <= rec.total_marks < 60:
                rec.scoring = 'maybe_in_future'
            elif 60 <= rec.total_marks < 80:
                rec.scoring = 'recommend'
            elif 80 <= rec.total_marks <= 100:
                rec.scoring = 'highly_recommend'
            else:
                rec.scoring = False

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            _logger.info(self.template_id.template_line_ids)
            _logger.info('self.template_iddddddddddddddddddddddddd')
            self.evaluation_line_ids = [(5, 0, 0)]
            self.evaluation_line_ids = [
                (0, 0, {
                    'evaluation_factors': line.evaluation_factors,
                    'initial_score': line.score,
                }) for line in self.template_id.template_line_ids
            ]


class EvaluationFormLines(models.Model):
    _name = 'evaluation.form.lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Evaluation Form Line'
    _rec_name = 'evaluation_factors'

    evaluation_id = fields.Many2one('evaluation.form', string="Evaluation Form", ondelete="cascade")
    evaluation_factors = fields.Char(string="Evaluation Factors")
    initial_score = fields.Selection(
        [('one', '1'), ('two', '2'), ('three', '3'), ('four', '4'), ('five', '5'), ('six', '6'), ('seven', '7'),
         ('eight', '8'), ('nine', '9'), ('ten', '10')], string="Initial Score", default=False)
    final_score = fields.Selection(
        [('one', '1'), ('two', '2'), ('three', '3'), ('four', '4'), ('five', '5'), ('six', '6'), ('seven', '7'),
         ('eight', '8'), ('nine', '9'), ('ten', '10')], string="Final Score", default=False)


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    @api.depends('partner_name', 'name')
    @api.depends_context('show_partner_name')
    def _compute_display_name(self):
        # if not self.env.context.get('show_partner_name'):
        #     return super()._compute_display_name()

        for applicant in self:
            if applicant.partner_name and applicant.name:
                applicant.display_name = f"{applicant.partner_name} - {applicant.name}"
            else:
                applicant.display_name = applicant.partner_name or applicant.name
