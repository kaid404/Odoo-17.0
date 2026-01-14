{
    'name': 'PAK GULF Attendance Reports ',
    'version': '17.0',
    'category': 'Studio',
    'summary': 'PAK GULF Employees Attendance Reports ',
    
    'license': 'AGPL-3',
    'module_type': 'official',
    'author': "ABDUL REHMAN GHANI (GXS)",
    'website': "http://www.globalxs.co/abdul.rehman@globalxs.co",
    'Maintainer': 'Global XS Technology Solutions',
    'depends': [
        'hr_attendance',
        'base', 'report_xlsx',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'reports/month_dept_wise_attend.xml',
        'reports/reports.xml',
        'wizard/month_dept_wise_attend.xml',
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
