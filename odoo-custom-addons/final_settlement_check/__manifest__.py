{
    'name': 'Final Settlement Check Field',
    'version': '17.0',
    'category': 'Extra Tools',
    'summary': 'Module for adding check field on Contract of Final Settlement',
    'sequence': '-10008',
    'license': 'AGPL-3',
    'author': 'GXS',
    'Maintainer': 'Odoo Mates',
    'website': '',
    'depends': [
        'hr',
        'hr_payroll',
        'hr_contract',
        'mail',
        'pakgulf_empl_final_settelment',
    ],
    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
