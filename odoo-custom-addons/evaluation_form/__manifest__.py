{
    'name': 'Evaluation Form',
    'version': '17.0',
    'category': 'Studio',
    'module_type': 'official',
    'summary': """ 
            Custom Odoo module to Evaluation Form.
    """,
    'author': 'HASNAIN JUTT(GXS)',
    'license': 'AGPL-3',
    'website': 'https://www.globalxs.co',
    'depends': ['hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'views/evaluation_form.xml',
        'views/evaluation_template.xml',
        'reports/evaluation_form_print.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
