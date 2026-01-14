import time

from odoo import models, api


class ReportAdmissionAnalysis(models.AbstractModel):
    _name = "report.gxs_admission.report_admission_analysis"
    _description = "Admission Analysis Report"

    def get_total_student(self, data):
        if data['course_id']:
            student_search = self.env['op.admission'].search_count(
                [('state', '=', 'done'),
                 ('course_id', '=', data['course_id'][0]),
                 ('admission_date', '>=', data['start_date']),
                 ('admission_date', '<=', data['end_date'])])
        else:
            student_search = self.env['op.admission'].search_count(
                [('state', '=', 'done'),
                 
                 ('admission_date', '>=', data['start_date']),
                 ('admission_date', '<=', data['end_date'])])
        return student_search

    def get_data(self, data):
        lst = []
        if data['course_id']:
            student_search = self.env['op.admission'].search(
                [('state', '=', 'done'),
                 ('course_id', '=', data['course_id'][0]),
                 ('admission_date', '>=', data['start_date']),
                 ('admission_date', '<=', data['end_date'])],
                order='admission_date desc')
        else:
            student_search = self.env['op.admission'].search(
            [('state', '=', 'done'),
             
             ('admission_date', '>=', data['start_date']),
             ('admission_date', '<=', data['end_date'])],
            order='admission_date desc')
        res = {}
        # self.total_student = 0
        total_student = 0
        for student in student_search:
            # self.total_student += 1
            total_student += 1
            res = {
                'name': student.name,
                'application_no': student.application_number,
            }
            lst.append(res)
        return lst

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'data': data,
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'get_total_student': self.get_total_student(data),
            'get_data': self.get_data(data),
        }
        return docargs
