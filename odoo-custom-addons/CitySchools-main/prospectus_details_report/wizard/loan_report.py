from pandas import to_datetime

from odoo import _, api, fields, models
from calendar import month_name
import datetime

import logging

_logger = logging.getLogger(__name__)


class CityProspectus(models.TransientModel):
    _name = 'city.prospectus.report'
    _description = "Vehicle Loan Report Wizard"

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    company_id = fields.Many2one('res.company', string="Company Name")
    user_id = fields.Many2one('res.users', string="Created By")



    def print_prospectus_report(self):
        from_month = month_name[self.from_date.month]
        from_year = self.from_date.year
        to_month = month_name[self.to_date.month]
        to_year = self.to_date.year



        domain = []
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.user_id:
            domain.append(('create_uid', '=', self.user_id.id))

        prospectus = self.env['op.prospectus'].search(domain)
        print(prospectus)
        uid_list = []
        for cr in prospectus.mapped('create_uid'):
            record_list = []
            for pros in prospectus.filtered(lambda x: x.create_uid.id == cr.id):
                record_list.append({
                    'from_date': self.from_date,
                    'to_date': self.to_date,
                    'application': pros.application_id.id,
                    'applicant_name': pros.applicant_name,
                    'father_name': pros.father_name,
                    'cnic': pros.guardian_cnic,
                    'amount': pros.amount,
                    'company': pros.company_id.name,
                    'register': pros.register_id.name,
                    'create': pros.create_uid.name,
                    'create_date': pros.create_date,
                })
            uid_list.append({
                'uid_name': cr.name,
                'record': record_list,
            })

        data = {
            'record_list': uid_list,
            'from_month': from_month,
            'to_month': to_month,
            'from_year': from_year,
            'to_year': to_year,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'company_name': self.env.company.name,
            'company_logo': self.env.company.logo,
        }

        return self.env.ref('prospectus_details_report.prospectus_details_report_action').report_action(self, data=data)