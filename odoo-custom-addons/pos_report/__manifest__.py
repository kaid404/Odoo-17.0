{
    'name': 'POS Receipt',
    'version': '17.0',
    'category': 'Point of Sale',
    'summary': 'Customize POS receipts.',
    'description': """
    """,
    'author': 'Global XS Technologies Solution',
    'depends': ['base', 'point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_report/static/src/**/*',
        ],
    },
    'data': [
        'reports/pos_receipt_report.xml',
    ],

    'license': 'AGPL-3',
    'sequence': 1,
    'installable': True,
    'application': False,
    'auto_install': False,
}
