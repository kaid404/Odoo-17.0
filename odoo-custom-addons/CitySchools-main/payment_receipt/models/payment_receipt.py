from odoo import api, models, _, fields
from num2words import num2words
from datetime import timedelta, datetime
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "op.admission"

    @api.model
    def prospect_amount_to_words(self, amount):
        """
        Convert a numeric amount into words.
        """
        return num2words(amount, lang='en').upper()
