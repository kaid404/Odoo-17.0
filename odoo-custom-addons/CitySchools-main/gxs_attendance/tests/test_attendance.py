from logging import info
import time
from .test_attendance_common import TestAttendanceCommon


class TestAttendanceRegister(TestAttendanceCommon):

    def setUp(self):
        super(TestAttendanceRegister, self).setUp()

    def test_case_attendance_register(self):
        register = self.op_attendance_register.search([])
        for record in register:
            info('      Attendance Register : %s' % record.name)
            info('      Course : %s' % record.course_id.name)
            info('      Code : %s' % record.code)


class TestAttendanceSheet(TestAttendanceCommon):

    def setUp(self):
        super(TestAttendanceSheet, self).setUp()

    def test_case_attendance_sheet(self):
        sheet = self.op_attendance_sheet.create({
            'name': 'AS',
            'attendance_date': time.strftime('%Y-%m-01'),
            'register_id':
                self.env.ref('gxs_attendance.'
                             'op_attendance_register_1').id
        })
        info('  Details Of Attendance Sheet:.....')
        for record in sheet:
            record.attendance_draft()
            record.attendance_start()
            record.attendance_done()
            record.attendance_cancel()


class TestAttendanceLine(TestAttendanceCommon):

    def setUp(self):
        super(TestAttendanceLine, self).setUp()

    def test_case_attendance_line(self):
        line = self.op_attendance_line.search([])
        info('  Details Of Attendance Lines:.....')
        for record in line:
            info('      Attendance Sheet : %s' % record.attendance_id.name)
            info('      Student : %s' % record.student_id.name)
            info('      Register : %s' % record.register_id.name)
            info('      Present : %s' % record.present)


class TestAttendanceWizard(TestAttendanceCommon):

    def setUp(self):
        super(TestAttendanceWizard, self).setUp()

    def test_case_attendance_wizard(self):
        student = self.op_attendance_wizard.create({
            'from_date': time.strftime('%Y-%m-01'),
            'to_date': time.strftime('%Y-%m-01')
        })
        student.print_report()
