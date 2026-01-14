from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class ReasonRelieving(models.Model):
    _name = 'reason.relieving'
    _description = 'reason.relieving'

    name = fields.Char('Reason')
