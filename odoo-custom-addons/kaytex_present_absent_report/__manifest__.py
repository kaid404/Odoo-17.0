# -*- coding: utf-8 -*-
{
    'name': "Kaytex Attendance Report",

    'summary': """
        Print Attendance Report for Employees""",

    'description': """
        This app helps you to print the attendances(Present and Absent Days) in PDF, based on Employees Calendar Resources.
    """,

    'author': "HCS",
    'website': "http://hcsgroup.io/",
    'company': 'Hafiz Consulting Services',
    'category': 'Employees',
    'version': '17.0',
    'depends': ['base', 'hr_attendance','hr'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        # 'views/templates.xml',
        'views/report_views.xml',
        'views/specific_employees.xml',
        # 'views/to_management_monthly_report.xml',
    ],
    "application": True,
    "installable": True,
}
