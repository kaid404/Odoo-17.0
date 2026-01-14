{
    'name': 'Attendance Summary Report',
    'version': '17.0',
    'category': 'HR',
    'summary': 'Attendance Summary Report',
    'depends': ['hr','hr_attendance'],
    'author': 'Khalid',
    'data': [
        'security/ir.model.access.csv',
        'views/att_summary_report_view.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
