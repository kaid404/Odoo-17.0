{
    'name': 'Salary XLSX Report',
    'version': '17.0',
    'author': "Khalid",
    'category': 'Reporting',
    'depends': ['hr_payroll', 'hr', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/salary_sheet_wizard_view.xml',
        'views/salary_sheet_report_action.xml',
    ],
    'installable': True,
}
