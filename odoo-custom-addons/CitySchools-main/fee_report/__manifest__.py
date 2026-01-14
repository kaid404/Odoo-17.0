{
    'name': 'Fee Report',
    'version': '17.0',
    'category': 'Productivity',
    'Summary': 'Fee Report',
    'depends': ['base'],
    'description': """Fee Report""",

    'data': [
        'security/ir.model.access.csv',
        'views/fee_report_wizard.xml',
        'views/fee_report.xml',

    ],
    'installable': True,
    'auto install': False,
}
