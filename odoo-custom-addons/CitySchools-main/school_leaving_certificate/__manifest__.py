
{
    'name': 'School Leaving Certificate',
    'version': '1.0',
    'category': 'studio',
    'module_type': 'official',
    'summary': """ 
            Fee module for schools and colleges to manage records of students who leave the school.
    """,
    'author': 'Mohsan Raza',
    'license': 'AGPL-3',
    'website': 'https://www.masho.co',
    'depends': ['base','gxs_core','mail','account','gxs_school_fee'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/school_leaving_certificate.xml',
        'views/student.xml',
        'views/account_move.xml',
        'reports/school_leaving_certificate_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
