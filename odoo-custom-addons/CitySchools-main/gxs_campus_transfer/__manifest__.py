{
    'name': 'Low Stock Notificaation',
    'version': '1.0',
    'category': 'Studio',
    'module_type': 'official',
    'summary': """ 
            Custom Odoo module to send an email of lows tock to related parson.
    """,
    'author': 'Abdul Jabbar',
    'license': 'AGPL-3',
    'website': 'https://www.globalxs.co',
    'depends': ['base','mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
