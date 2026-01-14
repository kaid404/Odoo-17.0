# -*- coding: utf-8 -*-
{
    'name': "City-School Books Sale Ledger Report (PDF)",
    'summary': """City-School Books Sale Ledger Report (PDF) """,
    'description': """Books Sale Ledger Report (PDF)""",
    'author': "ABDUL REHMAN GHANI (GXS)",
    'website': "http://www.globalxs.co/abdul.rehman@globalxs.co",
    'Maintainer': 'Global XS Technology Solutions',
    'category': 'Studio',
    'version': '1.0',
    'depends': [
        'stock',
        'sale',
        'purchase',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/city_books_ledger_template.xml',
        'wizard/city_books_ledger.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
