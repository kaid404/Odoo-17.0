from odoo import http
from odoo.http import request
from . import main
from datetime import date,datetime
class FacultyDashboardController(http.Controller):

    @http.route('/student_dashboard', type='http', auth="public", website=True, csrf=False, methods=['POST', 'GET'])
    def student_dashboard(self, **kw):

        # try:
        if 1==1:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                pass
                # return request.render("odoocms_web.portal_error", values)
            classes = []
            # academic_year
            # student_data = request.env['op.student'].sudo().search([('')])
            reg_course = request.env['op.student.course'].sudo().search([('student_id','=',student.id),
                                                                         ('academic_years_id','=',
                                                                          student.year_id.id),('academic_term_id',
                                                                                               '=',
                                                                                               student.class_id.id)],
                                                                        limit=1)
            values.update({
                'year':student.class_id.name,
                'class': student.year_id.name,
                'section': student.section_id.name,
                'reg_num':student.gr_no,
                'reg_course':reg_course

            })
            print(values)
            return http.request.render('student_portal.student_dashboard_template', values)
        # except Exception as e:
        #     values = {
        #         'error_message': e or False
        #     }
        #     # return http.request.render('odoocms_web.portal_error', values)

        # return request.render('student_portal.faculty_dashboard_template')

    @http.route('/fee', type='http', auth="public", website=True, csrf=False, methods=['POST', 'GET'])
    def attendance_template(self, **kw):
        values, success, student = main.prepare_portal_values(request)
        fee_data = request.env['account.move'].sudo().search([('student_id','=',student.id),('move_type','=',
                                                                                                    'out_invoice')],
                                                                    order='invoice_date asc')
        values.update({
            'fee_data':fee_data,
        })
        print(values)
        return request.render('student_portal.fee_template',values)


    @http.route('/student_profile', type='http', auth="public", website=True, csrf=False, methods=['POST', 'GET'])
    def profile_template_form(self, **kw):
        values, success, student = main.prepare_portal_values(request)
        if request.httprequest.method == 'GET':
            profile_form = request.env['op.student'].sudo().search([('id','=',student.id)], limit=1)
            return request.render('student_portal.student_profile_template', {
                'profile_form': profile_form,
            })
        return request.render('student_portal.student_profile_template')