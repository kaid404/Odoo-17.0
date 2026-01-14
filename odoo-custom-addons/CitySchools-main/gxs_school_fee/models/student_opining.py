from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import date,timedelta

class StudentFeeOpining(models.Model):
    _name = 'op.fee.opining'

    student_id  = fields.Many2one('op.student',string="Student")
    amount = fields.Float(string="Amount")
    status = fields.Char(string="Status")
