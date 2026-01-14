

{
    'name': 'GXS Parent',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Parent',
    'complexity': "easy",
    'author': 'Globalxs',
    'website': 'https://www.globalxs.co',
    'depends': ['gxs_core', 'gxs_exam'],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'data/parent_user_data.xml',
        'views/merksheet_lines_dup.xml',
        'views/parent_view.xml',
        'views/parent_relationship_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        'demo/res_partner_demo.xml',
        'demo/res_users_demo.xml',
        'demo/parent_relationship_demo.xml',
        'demo/parent_demo.xml',
    ],
    # 'images': [
    #     'static/description/openeducat_parent_banner.jpg',
    # ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
