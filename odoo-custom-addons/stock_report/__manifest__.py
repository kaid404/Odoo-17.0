# -*- coding: utf-8 -*-
{
    'name': "Stock Summary Report",

    'summary': """Stock Summary Report""",

    'description': """Stock Summary Report""",

    'author': "Khalid",
    'version': '17.0',

    'depends': ['base','point_of_sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',

    ],
    'installable': True,
    'application': True,
    'auto install': False,

}

