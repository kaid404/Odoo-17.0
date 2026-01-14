{
    'name': 'Attendance Analysis Report',
    'version': '17.0',
    'category': 'HR',
    'summary': 'Reports for Lates, Leaves & Absences',
    'depends': ['hr','hr_attendance'],
    'author': 'Khalid',
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_view.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
