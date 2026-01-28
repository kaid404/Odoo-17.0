{
    'name': 'Payslip Custom Report',
    'version': '17.0',
    'category': 'Human Resources',
    'summary': 'Custom Payslip Report with filters',
    'depends': ['base', 'hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/payslip_custom_report_views.xml',
        'views/payslip_custom_report_template.xml',
    ],
    'installable': True,
    'application': False,
}
