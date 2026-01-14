{
    'name': 'Blinq',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Auto link project task',
    'license': 'AGPL-3',
    'author': 'Abdul Jabbar',
    'Maintainer': 'Odoo',
    'website': 'odoomates.com',
    'depends': [
        'account',
        'gxs_core',
        'gxs_school_fee',
        'fee_discount'
    ],
    'demo': [],
    'data': [
        # 'data/auto_reallocation_cron.xml',
        # 'data/auto_reallocation_cron.xml',
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}