{
    'name': "Whatsapp Send Attachments",

    'summary': """

    """,

    'author': "Saad Ahmad",
    'website': 'https://www.globalxs.co',
    'support': 'mohsan.raza@globalxs.co',

    'category': 'Technical Settings',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','gxs_core'],

#     # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/account_move.xml',
        'views/student.xml',
        ],
#

    'installable': True,
    'auto_install': False,
    'price': 19.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
