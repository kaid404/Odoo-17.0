{
    'name': 'Supplier Advances XLS Report',
    'version': '1.0',
    'author': 'Asad',
    'category': 'Accounting',
    'summary': 'Unadjusted Suppliers Advances XLS Report',
    'depends': ['account', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/supplier_advances_xls_report_wizard.xml',
        'report/supplier_advances_report_menu.xml',
    ],
    'installable': True,
    'application': False,
}
