# -*- coding: utf-8 -*-
{
    'name': "Payslip Report Pakgulf",
    'summary': """Payslip Report Pakgulf""",
    'description': """Payslip Report Pakgulf""",
    'author': "Mohid Awan",
    'website': "http://www.globalxs.co",
    'category': 'Human Resource',
    'version': '17.0',
    'depends': [
        'hr', 'hr_payroll',
    ],
    'demo': [],
    'data': [
        # 'security/ir.model.access.csv',
        # 'wizard/employee_payslip_report_wizard_pakgulf.xml',
        'views/employee_payslip_report_template_pakgulf.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
