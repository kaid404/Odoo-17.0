{
    'name': 'CMS Student Portal',
    'version': '17.0',
    'summary': """CMS Student Portal""",
    'description': 'CMS Student Portal',
    'category': 'Portal',
    'sequence': 1,
    'author': 'Mohid',
    'company': 'GlobalXS Technology Solutions',
    'website': "https://www.globalxs.co/",
    'license': 'AGPL-3',
    'depends': ['base', 'website'],
    'data': [
        'views/faculty_dashboard.xml',
        'views/fee.xml',
        # 'views/attendance_form.xml',
        'views/profile.xml',
    ],
    'assets': {
            'web.assets_backend': [
                # '/student_portal/static/src/js/faculty_script.js',
            ],
            'web.assets_common': [
                # '/student_portal/static/src/js/faculty_script.js',
            ],
        },
    'installable': True,
    'auto_install': False,
    'application': True,
}
