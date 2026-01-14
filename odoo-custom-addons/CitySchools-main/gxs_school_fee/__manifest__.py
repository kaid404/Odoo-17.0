
{
    'name': 'Odoo Fee Module',
    'version': '1.0',
    'category': 'Accounting',
    'module_type': 'official',
    'summary': """ 
            Fee module for schools and colleges
    """,
    'author': 'Mohsan Raza',
    'license': 'AGPL-3',
    'website': 'https://www.globalxs.co',
    'depends': ['base','gxs_core','mail','stock','account'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/fee_structure.xml',
        'views/product.xml',
        'views/account_move.xml',
        'views/student.xml',
        'views/waiver.xml',
        'wizards/fee_wizards.xml',
        'wizards/split_invoice_view.xml',
        'views/student_opining.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
