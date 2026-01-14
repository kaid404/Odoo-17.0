from odoo import http
from odoo.http import request
import base64


class EmploymentApplicationPortal(http.Controller):

    @http.route('/employment/application', type='http', auth='public', website=True)
    def application_form(self, **kw):
        return http.request.render(
            'portal_employment_application.portal_employment_application_form', {}
        )

    @http.route('/employment/application/submit', type='http', auth='public', website=True, csrf=True)
    def application_submit(self, **post):
        vals = {
            'name': post.get('name'),
            'date_of_birth': post.get('date_of_birth'),
            'mobile_no': post.get('mobile_no'),
            'email_id': post.get('email_id'),
            'cnic_number': post.get('cnic_number'),
            'marital_status': post.get('marital_status'),
            'current_address': post.get('current_address'),
            'position_applied': post.get('position_applied') or False,
            'date': post.get('date'),
            'expected_salary': post.get('expected_salary'),
            'gross_salary': post.get('gross_salary'),
            'qualification_recent': post.get('qualification_recent'),
            'institute_name': post.get('institute_name'),
            'current_company': post.get('current_company'),
            'current_job': post.get('current_job'),
            'total_work_experience': post.get('total_work_experience'),
            'father_occupation': post.get('father_occupation'),
            'relatives_employed': post.get('relatives_employed'),
            'previously_employed': post.get('previously_employed'),
            'info_source': post.get('info_source'),
            'name_1': post.get('name_1'),
            'relationship_1': post.get('relationship_1'),
            'position_held_1': post.get('position_held_1'),
            'name_2': post.get('name_2'),
            'relationship_2': post.get('relationship_2'),
            'position_held_2': post.get('position_held_2'),
            # 'team_name': post.get('team_name'),
            # 'Interviewer_name': post.get('Interviewer_name'),
            # 'interview_status': post.get('interview_status'),
            # 'reason': post.get('reason'),
            # 'visa_status': post.get('visa_status'),
            # 'additional_uni_status': post.get('additional_uni_status'),
            # 'work_status_in_pk': post.get('work_status_in_pk'),
            # 'name_in_block_letter': post.get('name_in_block_letter'),
        }

        signature_file = request.httprequest.files.get('signature')
        if signature_file:
            vals['signature'] = base64.b64encode(signature_file.read())

        date_signature_file = request.httprequest.files.get('date_signature')
        if date_signature_file:
            vals['date_signature'] = base64.b64encode(date_signature_file.read())

        record = request.env['employment.form'].sudo().create(vals)

        return http.request.render(
            'portal_employment_application.portal_application_thank_you', {}
        )