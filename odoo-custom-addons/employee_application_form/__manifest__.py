
{
    'name': "Employee Application Form",

    'summary': "Employee Application Form",

    'description': """Employee Application Form""",

    'author': "Ali",
    'version': '18.0',

    'depends': ['mail','hr','hr_recruitment'],

    'data': [
        'security/ir.model.access.csv',
        'views/application_form.xml',
        'reports/employment_form_report.xml',
        'views/inherit_views.xml',
    ],
}

