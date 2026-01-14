# -*- coding: utf-8 -*-
{
    'name': "Student Fee Update",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """Update fee of Student""",

    'author': "Hamza",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'gxs_core', 'gxs_admission'],

    'data': [
        'security/ir.model.access.csv',
        'views/fee_view.xml',
        'views/category_view.xml',
    ],
}
