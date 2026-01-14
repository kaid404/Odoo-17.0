# -*- coding: utf-8 -*-

{
    'name': 'GXS ERP',
    'version': '17.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Students, Faculties and Education Institute',
    'complexity': "easy",
    'author': 'Globalxs',
    'website': 'https://www.globalxs.co',
    'depends': [
        'gxs_admission',
        'gxs_attendance',
        'gxs_parent',
        'gxs_exam',
        'gxs_attendance_roster',
    ],
    'images': [
        'static/description/openeducat_erp_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
