
{
    'name': 'Lock payments after certain time of the day',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Accounting',
    "sequence": 3,
    'summary': ' Payment Workflow',
    'complexity': "easy",
    'author': 'Globalxs',
    'website': 'https://www.globalxs.co',
    'depends': ['account'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/params.xml',
        'views/payment.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
