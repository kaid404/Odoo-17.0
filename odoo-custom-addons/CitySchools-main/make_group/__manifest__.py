
{
    'name': 'Make Group',
    'version': '17.0',
    'category': 'Invoice',
    'summary': """ 
             Module for schools and colleges
    """,
    'author': 'Haider Riaz',
    'license': 'AGPL-3',
    'website': 'https://www.globalxs.co',
    'depends': ['base','gxs_core','mail','stock'],
    'data': [

        'views/group.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
