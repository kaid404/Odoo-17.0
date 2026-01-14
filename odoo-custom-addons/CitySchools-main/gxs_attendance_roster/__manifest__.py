# -*- coding: utf-8 -*-
{
    'name': "GXS gGenerate Attendance Roaster",
    'summary': """Generate Attendance Roaster""",
    'description': """PGenerate Attendance Roaster""",
    'author': "ABDUL REHMAN GHANI (GXS)",
    'website': "http://www.globalxs.co/abdul.rehman@globalxs.co",
    'Maintainer': 'Global XS Technology Solutions',
    'category': 'Studio',
    'license': 'AGPL-3',
    'version': '1.0',
    'depends': [
        'gxs_attendance',
        'hr',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/generate_roster_view.xml',
        'wizard/view.xml',

    ],
    'installable': True,
    'application': True,
    'auto install': False,
}