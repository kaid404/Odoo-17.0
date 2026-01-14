# -*- coding: utf-8 -*-


{
    'name': 'GXS Fees',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Fees',
    'complexity': "easy",
    'author': 'Globalxs',
    'website': 'https://www.globalxs.co',
    'depends': ['gxs_core', 'account'],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'report/report_menu.xml',
        'report/fees_analysis_report_view.xml',
        'wizard/fees_detail_report_wizard_view.xml',
        'views/fees_terms_view.xml',
        'views/student_view.xml',
        'views/course_view.xml',
        'views/fees_element_view.xml',
        # 'menus/op_menu.xml',
    ],
    # 'images': [
    #     'static/description/openeducat_fees_banner.jpg',
    # ],
    'demo': [
        'demo/product_category_demo.xml',
        'demo/product_demo.xml',
        'demo/fees_element_line_demo.xml',
        'demo/fees_terms_line_demo.xml',
        'demo/fees_terms_demo.xml',
        'demo/course_demo.xml',
        'demo/student_fees_details_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
