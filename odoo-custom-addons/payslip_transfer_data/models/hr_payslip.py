from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    emp_department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    emp_job_id = fields.Many2one('hr.job', string='Designation', tracking=True)
    emp_location_id = fields.Many2one('hr.work.location', string='Location', tracking=True)
    emp_employee_grade = fields.Selection([
        ('1-A', '1-A'),
        ('1-C', '1-C'),
        ('1-D', '1-D'),
        ('2-A', '2-A'),
        ('2-B', '2-B'),
        ('3-A', '3-A'),
        ('3-B', '3-B'),
        ('3-C', '3-C'),
        ('4-A', '4-A'),
        ('4-B', '4-B'),
        ('4-C', '4-C'),
        ('4-D', '4-D'),
        ('5-A', '5-A'),
        ('5-B', '5-B'),
        ('5-C', '5-C'),
        ('6-A', '6-A'),
        ('6-B', '6-B'),
    ], string='Grade', default=False, tracking=True
    )
    emp_employee_type = fields.Selection([
        ('employee', 'Employee'),
        ('student', 'Student'),
        ('trainee', 'Trainee'),
        ('contractor', 'Contractor'),
        ('freelance', 'Freelancer'),
    ], string='Employee Type', default=False, tracking=True)
    emp_analytics = fields.Many2one('account.analytic.account', string='Analytics', tracking=True)
    emp_employee_bank = fields.Char(string='Employee Bank', tracking=True)
    emp_employer_bank = fields.Many2one('res.partner.bank', string='Employer Bank', tracking=True)
    

    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def _onchange_employee_id(self):
        _logger.info(self)
        for rec in self:
            _logger.info('-------------------------------')
            _logger.info(rec.employee_id)
            if rec.employee_id:
                rec.struct_id = rec.employee_id.contract_id.structure_type_id.default_struct_id.id
                # rec.x_studio_company_name = rec.employee_id.emp_company_id.id
                rec.emp_department_id = rec.employee_id.department_id
                rec.emp_job_id = rec.employee_id.job_id.id
                rec.emp_location_id = rec.employee_id.work_location_id.id
                rec.emp_employee_grade = rec.employee_id.x_studio_grade
                rec.emp_employee_type = rec.employee_id.employee_type
                rec.emp_analytics = rec.employee_id.contract_id.analytic_account_id.id
                rec.emp_employee_bank = rec.employee_id.bank_account
                rec.emp_employer_bank = rec.employee_id.company_bank_id.id
