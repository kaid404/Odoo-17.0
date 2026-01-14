from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class ApprovalCeo(models.Model):
    _name = 'approval.ceo'
    _description = 'approval_ceo'

    name = fields.Char('Approval')

