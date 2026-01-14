{
    'name': 'GXS Classroom',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Classroom',
    'complexity': "easy",
    'author': 'Globalxs',
    'website': 'https://www.globalxs.co',
    'depends': ['gxs_core', 'gxs_facility', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/classroom_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        'demo/classroom_demo.xml',
        'demo/facility_line_demo.xml'
    ],
    # 'images': [
    #     'static/description/openeducat_classroom_banner.jpg',
    # ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
