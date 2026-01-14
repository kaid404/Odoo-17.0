from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class BudgetInformation(models.Model):
    _name = 'budget.information'
    _description = 'budget_information'

    name = fields.Char('Budget')
