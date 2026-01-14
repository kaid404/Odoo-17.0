# -*- coding: utf-8 -*-
{
    'name': "Mail Templates",

    'summary': "Mail Templates for a company hiring process",

    'description': """Mail Templates for a company hiring process""",

    'author': "Kaid",

    'version': '17.0',

    'depends': ['hr_recruitment','mail'],

    'data': [
        'views/required_docs_template.xml',
        'views/internship_offer_template.xml',
        'views/candidate_shortlisted_template.xml',
        'views/job_offer_template.xml',
        'views/job_rejection_template.xml',
        'views/job_application_onhold.xml',
        'views/applicant_views.xml',
    ],
    "application": True,
    "installable": True,
}

