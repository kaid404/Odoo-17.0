from odoo import models, fields

class LeaveSummaryReportWizard(models.TransientModel):
    _name = 'leave.summary.report.wizard'
    _description = 'Leave Summary Report Wizard'

    report_type = fields.Selection([
        ('company', 'Company'),
        ('employees', 'Employees'),
        ('department', 'Department'),
        ('team', 'Team'),
    ], required=True)

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        readonly=True
    )

    employee_ids = fields.Many2many('hr.employee')
    department_ids = fields.Many2many('hr.department')
    team_ids = fields.Many2many('x_team')
    leave_type_ids = fields.Many2many('hr.leave.type')

    def print_report(self):
        return self.env.ref(
            'leave_summary_report.action_leave_summary_report'
        ).report_action(self)
