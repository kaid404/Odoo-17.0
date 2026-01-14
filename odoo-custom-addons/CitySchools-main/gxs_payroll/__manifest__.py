{
    'name': 'GXS Payroll',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Module for manging the draft attendance',
    'sequence': '-100',
    'license': 'AGPL-3',
    'author': 'Saad',
    'Maintainer': '',
    'website': '',
    'depends': [
        'hr_payroll','hr_contract'
    ],
    'demo': [],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
