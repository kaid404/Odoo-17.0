from odoo import _, api, fields, models
import calendar
import logging
from datetime import datetime ,date

_logger = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'
    is_teacher = fields.Boolean('Is Teacher')