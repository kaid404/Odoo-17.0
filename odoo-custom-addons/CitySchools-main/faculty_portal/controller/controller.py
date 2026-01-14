from odoo import http
from odoo.http import request
from . import main
from datetime import date, datetime
from datetime import datetime, timedelta
import pytz
from odoo import api, fields, models, _
import json

import logging


_logger = logging.getLogger(__name__)



class hrapplicant(models.Model):
    _inherit = 'op.session'

    def utc_time(self, time):
        return time + timedelta(hours=5)
        # local_tz = pytz.timezone('Asia/Karachi')  # Replace with your local timezone
        # local_time = local_tz.localize(time)
        # return local_time.astimezone(pytz.utc).time()


class FacultyDashboardController(http.Controller):

    @http.route('/dashboard', type='http', auth="public", website=True, csrf=False, methods=['POST', 'GET'])
    def faculty_dashboard(self, **kw):

        # try:
        if 1 == 1:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                pass
                # return request.render("odoocms_web.portal_error", values)
            classes = []
            attendances = []
            # academic_year
            all_classes = request.env['op.session'].sudo().search([('faculty_id', '=', faculty_staff.id),
                                                                   ('year_id.current_year', '=', True)])
            attendances_records = request.env['op.attendance.sheet'].sudo().search(
                [('faculty_id', '=', faculty_staff.id),
                 ('attendance_date', '=', date.today())])
            for att in attendances_records:
                attendances.append({
                    'course_id': att.course_id.name,
                    'faculty_id': faculty_staff.name,
                    'attendance_date': att.attendance_date,
                    'name': att.name
                })
            for rec in all_classes:
                if rec.start_datetime.date() == date.today():
                    classes.append(rec)
            work_load = all_classes.mapped('subject_id')
            barcode = faculty_staff.emp_id.barcode
            load = len(work_load)

            if faculty_staff.user_id:
                ttttttttttttt = str(faculty_staff.user_id.id)

            sql = """SELECT DISTINCT recipient_id FROM notification_recipient_rel WHERE user_id = """ + ttttttttttttt
            request.cr.execute(sql)
            returned_ids = request.cr.fetchall()
            recipient_list = []
            for rec in returned_ids:
                recipient_list.append(rec[0])
            notify = http.request.env["cms.notification"].sudo().search(
                [
                    ('visible_for', 'in', ['faculty']), ('id', 'in', recipient_list),
                    ("expiry", ">=", datetime.now()),
                ])

            values.update({
                'notify': notify,
                'classes': classes,
                'load': load,
                'barcode': barcode,
                'attendance': attendances
            })
            print(values)
            return http.request.render('faculty_portal.faculty_dashboard_template', values)
        # except Exception as e:
        #     values = {
        #         'error_message': e or False
        #     }
        #     # return http.request.render('odoocms_web.portal_error', values)

        # return request.render('faculty_portal.faculty_dashboard_template')

    @http.route(
        "/notification",
        type="http",
        auth="user",
        website=True,
        csrf=False,
        methods=["POST", "GET"],
    )
    def notification(self, **kw):
        login = request.env.user.name
        faculty_staff = request.env.user.employee_id
        # business_unit = faculty_staff.department_id.bussiness_unit_id.name

        values = {}
        sql = """SELECT DISTINCT recipient_id FROM notification_recipient_rel WHERE user_id = """ + str(
            faculty_staff.user_id.id)
        request.cr.execute(sql)
        returned_ids = request.cr.fetchall()
        recipient_list = []
        for rec in returned_ids:
            recipient_list.append(rec[0])
        bell = http.request.env["cms.notification"].sudo().search(
            [
                ('visible_for', 'in', ['faculty']), ('id', 'in', recipient_list),
                ("expiry", ">=", datetime.now()),
            ])
        notif = http.request.env["cms.notification"].sudo().search(
            [("visible_for", "=", ["employee", "event", 'faculty']), ('id', 'in', recipient_list), ("expiry", ">=",
                                                                                                    datetime.now())])
        # bell = http.request.env["cms.notification"].sudo().search(
        #     [("visible_for", "=", ["employee", "all"]), ("expiry", ">=", datetime.now()), ])
        # xcf = http.request.env['hr.employee'].sudo().search(
        #     [('work_contact_id', '=', request.env.user.partner_id.id)], limit=1)
        # # if xcf.user_id.user_type == 'faculty':
        # #     emp = 1
        # # else:
        # #     emp = 0
        #
        # if xcf.user_id.has_group('base.group_user'):
        #     internal_user = 1
        # else:
        #     internal_user = 0
        values.update(
            {
                "notify": notif,
                # "emp": emp,
                # "internal_user": internal_user,
                # "att": notif,
                # "name": faculty_staff.name,
                # "job_id": faculty_staff.job_id.name,
                # "pic": faculty_staff.image_1920,
                "bell": bell,
                # "log": login
            }
        )
        return http.request.render(
            "faculty_portal.notification_template", values
        )

    @http.route('/attendance', type='http', auth="public", website=True, csrf=False, methods=['POST', 'GET'])
    def attendance_template(self, **kw):
        values, success, faculty_staff = main.prepare_portal_values(request)
        attendance_data = request.env['op.attendance.sheet'].sudo().search([('faculty_id', '=', faculty_staff.id),
                                                                            ('attendance_date', '=', date.today())])

        print(attendance_data)
        values.update({
            'attendance_data': attendance_data,
        })
        print(values)
        return request.render('faculty_portal.attendance_template', values)

    @http.route('/attendance_form/<int:id>', type='http', auth="public", website=True, csrf=False,
                methods=['POST', 'GET'])
    def attendance_form_template(self, id=0, **kw):
        print(id)
        attendance_sheet = request.env['op.attendance.sheet'].sudo().search([('id', '=', id)], limit=1)
        if request.httprequest.method == 'GET':
            # Retrieve the attendance sheet data for the form

            return request.render('faculty_portal.attendance_form_template', {
                'attendance_sheet': attendance_sheet,
            })

        elif request.httprequest.method == 'POST':
            # Handle form submission and update attendance lines
            attendance_sheet_id = int(kw.get('attendance_sheet_id'))
            # attendance_sheet = request.env['op.attendance.sheet'].browse(attendance_sheet_id)

            print(kw)
            for line_id in attendance_sheet.attendance_line:
                val = {
                    'present': False,
                    'late': False,
                    'excused': False,
                    'absent': False,
                    'remark': '',
                }
                for key, value in kw.items():
                    if key.startswith('attendance_'):
                        if key == f"attendance_present_{line_id.id}":
                            val['present'] = True
                        if key == f"attendance_late_{line_id.id}":
                            val['late'] = True
                        if key == f"attendance_excused_{line_id.id}":
                            val['excused'] = True
                        if key == f"attendance_absent_{line_id.id}":
                            val['absent'] = True
                        if key == f"attendance_remark_{line_id.id}":
                            val['remark'] = value

                line_id.write(val)

            # Redirect to the attendance page after updating
            return request.redirect('/attendance')

    @http.route('/profile', type='http', auth="public", website=True, csrf=False, methods=['POST', 'GET'])
    def profile_template_form(self, **kw):
        values, success, faculty_staff = main.prepare_portal_values(request)
        if request.httprequest.method == 'GET':
            profile_form = request.env['op.faculty'].sudo().search([('id', '=', faculty_staff.id)], limit=1)
            return request.render('faculty_portal.profile_template', {
                'profile_form': profile_form,
            })
        return request.render('faculty_portal.profile_template')

    @http.route('/diary_form', type='http', auth="public", website=True, csrf=False, methods=['POST', 'GET'])
    def faculty_diary_form_template(self, **kw):
        values, success, faculty_staff = main.prepare_portal_values(request)

        if request.httprequest.method == 'GET':
            dairy_record = request.env['faculty.diary'].sudo().search([])

            diary_lines = request.env['faculty.diary.line'].sudo().search(
                [('class_id', 'in', dairy_record.ids)]) if dairy_record else []

            return request.render('faculty_portal.diary_form_template', {
                'diary_rec': dairy_record,
                'diary_lines': diary_lines,
            })

        return request.render('faculty_portal.diary_form_template')

    @http.route('/diary', type='http', auth="public", website=True, csrf=False, methods=['POST', 'GET'])
    def diary_template_form(self, **kw):
        values, success, faculty_staff = main.prepare_portal_values(request)

        if request.httprequest.method == 'GET':
            class_ids = request.env['op.academic.year'].sudo().search([])
            print('class_ids-->', class_ids)

            course_ids = request.env['op.course'].sudo().search([('class_id', 'in', class_ids.ids)]) if class_ids else []
            print('course_ids-->', course_ids)

            return request.render('faculty_portal.diary_template', {
                'class_ids': class_ids,
                'course_ids': course_ids,
            })

        return request.render('faculty_portal.diary_template')

    @http.route('/get_subjects_by_class', type='http', auth="public", methods=['POST','GET'], csrf=False)
    def get_subjects_by_class(self, **kw):
        data = json.loads(request.httprequest.data)
        # class_id = request.httprequest.headers.get('class_id')
        class_id = data.get('class_id')
        print('class_id---->', kw)
        print('class_id---->', class_id)
        _logger.info(f"{class_id}//////")

        if class_id:
            courses = request.env['op.course'].sudo().search([('class_id', '=', int(class_id))])
            print('courses--->>>', courses)
            subjects_data = []
            for course in courses:
                for subject in course.subject_ids:
                    subjects_data.append({
                        'name': subject.name,
                        'class_id': course.name,
                    })
            print('subjects_data--->', subjects_data)
            _logger.info(f"{class_id}//////{courses}")
            return json.dumps({'subjects': subjects_data})
        return json.dumps({'error': 'No class_id provided'})

    @http.route('/submit_diary', type='http', auth="public", methods=['POST'], csrf=False)
    def submit_diary(self, **post):
        class_id = post.get('class_select')
        print('class_id--->>>', class_id)

        subject_names = request.httprequest.form.getlist('subject_name[]')
        class_names = request.httprequest.form.getlist('class_name[]')
        descriptions = request.httprequest.form.getlist('description[]')

        print('subject_names---->', subject_names)
        print('class_names---->', class_names)
        print('descriptions----->', descriptions)

        if not class_id or not subject_names or not class_names or not descriptions:
            return request.redirect('/diary_form')

        diary = request.env['faculty.diary'].sudo().create({
            'name': 'Diary Entry for Class {}'.format(class_id),
        })

        for subject_name, class_name, description in zip(subject_names, class_names, descriptions):
            if subject_name and class_name and description:
                request.env['faculty.diary.line'].sudo().create({
                    'subject': subject_name,
                    'class_id': class_name,
                    'date': date.today(),
                    'description': description,
                    'diary_id': diary.id,
                })

        return request.redirect('/diary_form')

