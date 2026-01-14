
{
    'name': 'Employee Schedule Report',
    'version': '1.0',
    'category': 'Human Resources',
    'depends': ['hr_attendance','hr','report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_schedule_report_view.xml',
        'views/employee_schedule_report.xml',
    ],
    'installable': True,
    'application': True,
}
