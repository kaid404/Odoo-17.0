{
    'name': 'Employee Activity Report',
    'version': '17.0',
    'category': 'Reporting',
    'summary': 'Employee Activity Report',
    'depends': ['hr','hr_attendance'],
    'author': 'Khalid',
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_view.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
