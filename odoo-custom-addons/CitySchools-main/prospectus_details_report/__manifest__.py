# -*- coding: utf-8 -*-
{
    'name': "Prospectus Details Report (PDF)",
    'summary': """Prospectus Details Report (PDF)""",
    'description': """Prospectus Details Report (PDF)""",
    'author': "Global XS Technology Solutions",
    'website': "http://www.globalxs.co",
    'category': 'Studio',
    'license': 'AGPL-3',
    'version': '17.0',
    'module_type': 'official',
    'depends': [
        'gxs_admission',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/loan_report_template.xml',
        'wizard/loan_report_wizard.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
