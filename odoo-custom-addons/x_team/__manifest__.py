{
    'name': 'Employee Teams',
    'version': '17.0',
    'category': 'Human Resources',
    'summary': 'Add Teams to Employees',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/x_team_views.xml',
    ],
    'installable': True,
    'application': False,
}
