from dateutil.relativedelta import relativedelta
from odoo import fields, models, api


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]

    def _get_employees(self):
        active_employee_ids = self.env.context.get('active_employee_ids', False)
        if active_employee_ids:
            return self.env['hr.employee'].browse(active_employee_ids)
        # YTI check dates too
        emps =  self.env['hr.employee'].search(self._get_available_contracts_domain()).ids
        final_sat_emps =  self.env['employee.final.settlement'].search([]).mapped('name.id')
        e = list(set(emps) - set(final_sat_emps))
        return self.env['hr.employee'].search([('id','in',e)])



class HrEmployee(models.Model):
    _name = 'employee.final.settlement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Final Settlement'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('1st_appr', '1st Approval'),
        ('2nd_appr', '2nd Approval'),
        ('payslip', 'Payslip'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', copy=True, tracking=True)
    name = fields.Many2one('hr.employee', string="Name", store=True, tracking=True)
    batch = fields.Char(string="Badge ID", store=True, compute='_compute_employee_details', tracking=True)
    company = fields.Char(string='Company', store=True, compute='_compute_employee_details', tracking=True)
    department = fields.Char(string='Department', store=True, compute='_compute_employee_details', tracking=True)
    designation = fields.Char(string='Designation', store=True, compute='_compute_employee_details', tracking=True)
    structure_type = fields.Char(string='Final Settlement Structure Type', store=True,
                                 compute='_compute_employee_details', tracking=True)
    emp_bank_name = fields.Char(string='Employee Bank Name', store=True, compute='_compute_employee_details',
                                tracking=True)
    emp_acc_no = fields.Char(string='Account #', store=True, compute='_compute_employee_details', tracking=True)
    grade = fields.Char(string='Grade', store=True, compute='_compute_employee_details', tracking=True)
    location = fields.Char(string='Location', store=True, compute='_compute_employee_details', tracking=True)
    dob = fields.Char(string='Birth Date', store=True, compute='_compute_employee_details', tracking=True)
    jod = fields.Char(string='Joining Date', store=True, compute='_compute_employee_details', tracking=True)
    gratuity_date = fields.Date(string='Gratuity Date', compute='_compute_employee_details', store=True, tracking=True)
    leave_reason = fields.Many2one('hr.departure.reason', string='Leaving Reason', store=True, tracking=True)
    resign_date = fields.Date(string="Payslip Date", store=True, tracking=True)
    last_work_date = fields.Date(string="Last Working Date", tracking=True)
    count_days = fields.Integer(string="Worked Days", compute='_compute_days_from_start_of_month', store=True)
    pf_end_date = fields.Date(string="PF End Date", tracking=True)
    basic_salary = fields.Boolean(string="Basic Salary", store=True, tracking=True)
    notice_pay = fields.Boolean(string="Notice Pay", store=True, tracking=True)
    gratuity = fields.Boolean(string="Gratuity", store=True, tracking=True)
    pf_loan = fields.Boolean(string="PF Loan", store=True, tracking=True)
    comp_loan = fields.Boolean(string="Comp Loan", store=True, tracking=True)
    vehicle_loan = fields.Boolean(string="Vehicle Loan", store=True, tracking=True)
    prov_fund = fields.Boolean(string="Provident Fund", store=True, tracking=True)
    remarks = fields.Char(string='Remarks', store=True, tracking=True)
    payslip_id = fields.Many2one('hr.payslip', string='Payslip')
    button_clicked = fields.Boolean(default=False)

    @api.onchange('resign_date')
    def _onchange_resign_date(self):
        if self.resign_date:
            self.pf_end_date = self.resign_date
        else:
            self.pf_end_date = False

    @api.onchange('last_work_date')
    def _onchange_last_work_date(self):
        if self.last_work_date:
            self.name.contract_id.date_end = self.last_work_date
        else:
            self.name.contract_id.date_end = False

    @api.depends('last_work_date')
    def _compute_days_from_start_of_month(self):
        for record in self:
            if record.last_work_date:
                last_work_date = fields.Date.from_string(record.last_work_date)
                first_day_of_month = last_work_date.replace(day=1)
                days_diff = (last_work_date - first_day_of_month).days + 1
                record.count_days = days_diff
            else:
                record.count_days = 0

    @api.depends('name')
    def _compute_employee_details(self):
        for record in self:
            if record.name:
                record.batch = record.name.barcode
                # record.company = record.name.emp_company_id.name
                record.department = record.name.department_id.name
                record.designation = record.name.job_id.name
                record.structure_type = record.name.contract_id.final_settlement_structure.default_struct_id.name
                # record.emp_bank_name = record.name.bank_name
                # record.emp_acc_no = record.name.bank_account
                # record.grade = record.name.contract_id.x_studio_employee_grade
                record.location = record.name.work_location_id.name
                record.dob = record.name.birthday
                record.jod = record.name.contract_id.date_start
                record.gratuity_date = record.name.contract_id.date_start
            else:
                record.batch = False
                record.company = False
                record.department = False
                record.designation = False
                record.structure_type = False
                record.emp_bank_name = False
                record.emp_acc_no = False
                record.grade = False
                record.location = False
                record.dob = False
                record.jod = False
                record.gratuity_date = False

    def action_1st_appr(self):
        self.state = '1st_appr'

    def action_2nd_appr(self):
        self.state = '2nd_appr'

    def action_payslip(self):
        if self.resign_date:
            resign_date = fields.Date.from_string(self.resign_date)
            date_from = resign_date.replace(day=1)
            date_to = date_from + relativedelta(months=1, days=-1)

            payslip_name = f'Payslip for {self.name.name} ({date_from.strftime("%B %Y")})'
            structure = self.env['hr.payroll.structure'].search([('name', '=', self.structure_type)], limit=1)
            if not structure:
                raise ValueError(f'Payroll Structure "{self.structure_type}" not found')

            payslip_vals = {
                'name': payslip_name,
                'employee_id': self.name.id,
                'date_from': date_from,
                'date_to': date_to,
                'contract_id': self.name.contract_id.id,
                'struct_id': structure.id,
                'final_settlement_id': self.id,
                'emp_bank_name': self.emp_bank_name,
                'emp_acc_no': self.emp_acc_no,
                'last_work_date': self.last_work_date,
                'count_days': self.count_days,
            }
            payslip = self.env['hr.payslip'].create(payslip_vals)
            self.state = 'payslip'
            self.payslip_id = payslip.id

    def action_cancel(self):
        self.state = 'cancel'

    def action_reset(self):
        self.state = 'draft'

    def action_update(self):
        if self.resign_date:
            resign_date = fields.Date.from_string(self.resign_date)
            date_from = resign_date.replace(day=1)
            date_to = date_from + relativedelta(months=1, days=-1)

            payslip_name = f'Payslip for {self.name.name} ({date_from.strftime("%B %Y")})'
            structure = self.env['hr.payroll.structure'].search([('name', '=', self.structure_type)], limit=1)
            if not structure:
                raise ValueError(f'Payroll Structure "{self.structure_type}" not found')

            payslip_vals = {
                'name': payslip_name,
                'employee_id': self.name.id,
                'date_from': date_from,
                'date_to': date_to,
                'contract_id': self.name.contract_id.id,
                'struct_id': structure.id,
                'final_settlement_id': self.id,
                'emp_bank_name': self.emp_bank_name,
                'emp_acc_no': self.emp_acc_no,
                'last_work_date': self.last_work_date,
                'count_days': self.count_days,
            }
            self.payslip_id.write(payslip_vals)

    def action_archive(self):
        for record in self:
            if record.state == 'paid':
                employee = record.name
                if employee:
                    employee.active = False
                    employee.contract_ids.write({
                        'active': False,
                        'state': 'close',
                    })
                    record.button_clicked = True

                    return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_open_payslip(self):
        return {
            'name': 'Payslip',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'form',
            'domain': [('employee_id', '=', self.name)],
            'res_id': self.payslip_id.id,
            'target': 'current',
        }
