# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Attendance Adjust Request",
    'summary': """Attendance Adjust Request """,
    'description': """

    """,
    'category': 'Attendance',
    'author': 'Khalid',
    'version': '17.0',
    'depends': ['hr', 'hr_attendance', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'security/data.xml',
        'views/adjustment_views.xml',
    ],
    # 'js': ['static/src/js/attendance_adjustment.js'],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
