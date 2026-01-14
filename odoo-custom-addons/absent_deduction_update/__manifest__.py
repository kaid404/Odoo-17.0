# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Absent Deduction Amount Calculation",
    'summary': """ Add days field in global inputs to compute amount automatically""",
    'description': """

    """,
    'category': '',
    'version': '17.0',
    'module_type': 'official',
    'depends': ['hr_payroll','payroll_overtime_inputs'],

    'data': [
        'views/views.xml',
    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
