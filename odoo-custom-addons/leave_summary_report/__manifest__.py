{
    'name': 'Leave Summary Report',
    'version': '17.0.1.0.0',
    'category': 'HR',
    'summary': 'Leave Summary Report Wizard',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_wizard_view.xml',
        'views/report_template.xml',
    ],
    'installable': True,
}
