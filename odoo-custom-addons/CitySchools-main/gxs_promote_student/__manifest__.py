
{
    'name': 'Promote Students',
    'version': '1.0',
    'category': 'Education',
    'module_type': 'official',
    'summary': """ 
            Promote Students from one class to next!
    """,
    'author': 'Global XS Technology Solutions',
    'license': 'AGPL-3',
    'website': 'https://www.globalxs.co',
    'depends': ['base','gxs_core'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/promote_students.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
