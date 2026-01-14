from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from datetime import datetime, date, timedelta, time
import pytz
from datetime import date
import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
logger = logging.getLogger(__name__)

class EvaluationTemplate(models.Model):
    _name = "evaluation.template"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Evaluation Template'
    _rec_name = 'name'

    name = fields.Char(string="Template Name",
                       store=True, tracking=True, copy=False, required=True)

    template_line_ids = fields.One2many('evaluation.template.lines', 'template_id', string="Template Lines")


class EvaluationTemplateLines(models.Model):
    _name = 'evaluation.template.lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Evaluation Template Line'
    _rec_name = 'evaluation_factors'

    template_id = fields.Many2one('evaluation.template', string="Template")
    evaluation_factors = fields.Char(string="Evaluation Factors")
    score = fields.Selection(
        [('one', '1'), ('two', '2'), ('three', '3'), ('four', '4'), ('five', '5'), ('six', '6'), ('seven', '7'),
         ('eight', '8'), ('nine', '9'), ('ten', '10')], string="Score", default=False)
