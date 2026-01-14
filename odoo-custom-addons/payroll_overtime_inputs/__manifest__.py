# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Global Inputs Solution",
    'summary': """ Add manual inputs without going into payslips""",
    'description': """

    """,
    'category': '',
    'version': '1.0',
    'module_type': 'official',
    'depends': ['hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/global_inputs.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
