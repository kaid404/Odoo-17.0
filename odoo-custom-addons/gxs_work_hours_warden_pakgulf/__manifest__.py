{
    'name': "Ghani Attendance",
    'author': 'GlobalXS technology Solutions',
    'category': 'CRM',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': """
""",
    'version': '1.0',
    'depends': ['hr_attendance', 'hr_payroll', 'hr_holidays','planning',
        ],
    'data': [
        'security/ir.model.access.csv',
        # 'security/group.xml'
        'views/attendance_adjustment_views.xml',
        'views/late_policy.xml',
        'views/overtime.xml',
        'views/employee_gatepass.xml',
        'views/absent.xml',
        'views/letw_deduction.xml',

        # 'views/outdoor_work.xml',
        # 'views/remote_work.xml',
        # 'views/assumption_request.xml',
        # 'views/shift_change_request.xml',
        # 'views/settings.xml',
        # 'views/attendance_request.xml',

        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
