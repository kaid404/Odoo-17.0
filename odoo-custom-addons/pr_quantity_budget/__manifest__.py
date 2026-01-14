{
    'name': 'Purchase Request Quantity Budget',
    'version': '17.0',
    'category': 'Extra Tools',
    'summary': 'Purchase Request Quantity Budget',
    'sequence': '-1001',

    'license': 'AGPL-3',
    'author': 'Hammad Asghar (GXS)',

    'website': 'https://globalxs.co/',
    'depends': [
        'stock_request_approve_button_pakgulf',
        'purchase_request',
        'mail',
        'base',
        'stock',
        'stock_department',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        # 'views/menu.xml',
        'views/view.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
