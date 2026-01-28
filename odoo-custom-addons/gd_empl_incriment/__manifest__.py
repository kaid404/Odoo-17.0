{
    'name': 'Game District Employee Incriment',
    'version': '17.0',
    'category': 'contract',
    'author': 'Global Xs Tecnology Solution',
    'website': 'http://www.globalxs.co',
    'license': 'LGPL-3',
    'depends': ['base', 'hr','hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/paper_format.xml',
        'views/gd_empl_incriment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
