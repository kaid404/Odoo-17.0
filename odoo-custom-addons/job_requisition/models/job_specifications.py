from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class JobSpecifications(models.Model):
    _name = 'job.specifications'
    _description = 'job.specifications'

    name = fields.Char('Role Requirements')
