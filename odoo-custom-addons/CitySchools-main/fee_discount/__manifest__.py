{
    'name': 'Fee Discount',
    'version': '1.0',
    'category': 'Productivity',
    'Summary': 'Fee Discount',
    'module_type': 'official',
    'depends': ['gxs_school_fee'],
    'description': """Fee Discount""",

    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/fee_discount.xml',
        'views/account_move.xml',
        'views/wizard/fee_discount_wizard.xml',
    ],
    'installable': True,
    'auto install': False,
}
