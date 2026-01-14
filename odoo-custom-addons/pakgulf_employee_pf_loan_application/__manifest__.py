# -*- coding: utf-8 -*-
{
    'name': "Pak-Gulf APPLICATION FOR GRANT Of LOAN/ADVANCE To STAFF",
    'summary': """Pak-Gulf APPLICATION FOR GRANT Of LOAN/ADVANCE To STAFF ( Employee-Wise )""",
    'description': """Pak-Gulf APPLICATION FOR GRANT Of LOAN/ADVANCE To STAFF ( Employee-Wise )""",
    'author': "ABDUL REHMAN GHANI (GXS)",
    'website': "http://www.globalxs.co/abdul.rehman@globalxs.co",
    'Maintainer': 'Global XS Technology Solutions',
    'category': 'Studio',
    'version': '17.0',
    'depends': [
        'sync_employee_advance_salary', 'hr_payroll',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/emp_grant_loan_advance_template.xml',
        'wizard/emp_loan_payment_schedule_template.xml',
        'wizard/emp_contribution_loan_details_template.xml',
        'wizard/emp_grant_loan_advance.xml',
        'wizard/emp_loan_payment_schedule.xml',
        'wizard/emp_contribution_loan_details.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
