from odoo import models, fields, api, _,registry
from odoo.exceptions import ValidationError
from datetime import datetime

from dateutil.relativedelta import relativedelta
from datetime import datetime, time, timedelta,date



class AttendanceAdjustment(models.Model):
    _inherit = 'attendance.adjustment'
    _description = 'Attendance Adjustment Request'
    # _inherit = ['hr.attendance']

    emp_check_in_pre = fields.Datetime(string="Previous Check In")
    emp_check_out_pre = fields.Datetime(string="Previous Check Out")
    att_date = fields.Date(string='Date',required=True )
    from_date = fields.Date('From Date', default=lambda self: fields.Date.to_string(datetime.today().replace(day=1)),
                            required=True)
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1))), required=True)

    @api.onchange('att_date')
    def onchange_date(self):
        print('kk')
        search_attendance = self.env['hr.attendance']

        search_record = search_attendance.search(
            [('employee_id', '=', self.name.id), ('checkin_date', '=', self.att_date)])
        for rec in search_record:
            self.emp_check_in = rec.check_in
            self.emp_check_out = rec.check_out
    @api.constrains('att_date')
    def get_per_att(self):
        search_attendance = self.env['hr.attendance']
        for recs in self:
            search_record = search_attendance.search(
                [('employee_id', '=', recs.name.id), ('checkin_date', '=', recs.att_date)])


            for rec in search_record:
                recs.emp_check_in_pre = rec.check_in
                recs.emp_check_out_pre = rec.check_out
    def create_attendance(self):
        if self.state == 'approve':
            # dbname = self._cr.dbname
            # print(dbname)
            # cr = registry(dbname).cursor()
            # # cr.commit()
            #
            # print('workkkkkkkkkkkkk')
            # ttendance = self.env["hr.attendance"].search(
            #     [('employee_id', '=', self.name.id),
            #      ('checkin_date', '=', self.att_date)])
            # # ttendance.write({'assumption_request': 'Request Approved'
            # #                  })
            count_late = self.env["late.check_in"].search(
                [('employee_id', '=', self.name.id), ('date', '=', self.att_date)
                 ])
            print('lllllllllllllllllllllllllll',count_late)
            if count_late:
                print('lllllllllllllllllllllllllll', count_late.date)
                # count_late.sudo().unlink()
                try:
                    self.env.cr.execute("delete from late_check_in where id=%s" % count_late.id)
                except:
                    print('lllllllllllllllllllllllllll')
            duplicate = self.env["hr.leave"].search(
                [('employee_id', '=', self.name.id), ('date_from', '=', self.att_date),
                 ('name', '=', 'Late Deduction')
                 ],limit=1, order='id desc')

            if duplicate:
                print(duplicate.name,8888888888888888888888)
                try:
                    duplicate.action_refuse()
                    duplicate.action_draft()
                    # duplicate.sudo().unlink()
                    self.env.cr.execute("delete from hr_leave where id=%s" % duplicate.id)
                    # self.env.cr.commit()
                    print('lllllllllllllllllllllllllll')
                except:
                    pass

            # count_request = self.env['attendance.adjustment'].search_count([('name','=',self.name.id),
            #                                                           ('emp_check_in', '>=', self.from_date),
            #
            #                                                           ('emp_check_in', '<=', self.to_date),
            #                                                           ])
            # print(count_request,'count_request')
            # if count_request > 3:
            #     print('work')
            #     list_leave_type = ['Casual Leave','Sick leave', 'Annual Leave']
            #     for type in list_leave_type:
            #
            #         leave_by_type = self.env['hr.leave.allocation'].search(
            #             ['&', ('holiday_status_id', '=', type), ('employee_id', '=', self.name.id)])
            #         print(leave_by_type,type)
            #         if leave_by_type:
            #             date_leave_alocation = leave_by_type[0].date_from
            #         if not leave_by_type:
            #             date_leave_alocation = leave_by_type.date_from
            #         causal_leave = self.env["hr.leave"].search(
            #             [('employee_id', '=', self.name.id), ('date_from', '>=', date_leave_alocation),
            #              ('state', '=', 'validate')
            #
            #              ])
            #         duration = 0
            #         for i in causal_leave:
            #             duration = duration + i.number_of_days
            #
            #         # totaol_leave = leave_by_type.number_of_days_display - duration
            #         if leave_by_type:
            #             totaol_leave = leave_by_type[0].number_of_days_display - duration
            #         if not leave_by_type:
            #             totaol_leave = leave_by_type.number_of_days_display - duration
            #         leave_id = self.env['hr.leave.type'].search(
            #             [('name', '=', type)])
            #         # duplicate = self.env["hr.leave"].search_count(
            #         #     [('employee_id', '=', self.name.id), ('date_from', '=', date_day),
            #         #      ('holiday_status_id', '=', leave_id.id)
            #         #      ])
            #         causal_leave = self.env["hr.leave"].search(
            #             [('employee_id', '=', self.name.id), ('date_from', '>=', date_leave_alocation),
            #              ('state', '=', 'validate')
            #
            #              ])
            # leave_id = self.env['hr.leave.type'].search(
            #             [('name', '=', 'Short leave')])
            # id=self.env['hr.leave'].create({
            #     'employee_id': self.name.id,
            #     'date_from': self.att_date,
            #     'date_to': self.att_date,
            #     'request_date_from': self.att_date,
            #     'request_date_to': self.att_date,
            #     'holiday_status_id': leave_id.id,
            #     'number_of_days': 0.5,
            #     'name': 'Attendance Change Request',
            #
            # })
            # id.action_validate()

            #         duplicate = self.env["hr.leave"].search_count(
            #             [('employee_id', '=', self.name.id), ('date_from', '=', self.att_date),
            #              ('name', '=', 'Attendance Change Request')
            #              ])
            #
            #         if not duplicate:
            #             print('lllllljjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj')
            #             # half_day_salary = per_day_salary / .5
            #             self.env['late.check_in'].sudo().create({
            #                 'employee_id': self.name.id,
            #                 # 'late_minutes': rec.late_emp,
            #                 'date': self.att_date,
            #                 # 'attendance_id': self.id,
            #                 'amount': 1,
            #                 'description': 'Attendance Change Request',
            #
            #             })
            #
            #         # half_day_salary = per_day_salary / .5
            #         # self.env['late.check_in'].sudo().create({
            #         #     'employee_id': rec.employee_id.id,
            #         #     'late_minutes': rec.late_emp,
            #         #     'date': rec.check_in.date(),
            #         #     'attendance_id': rec.id,
            #         #     'amount': 0.5,
            #         #     'description': 'Deduction from salary',
            #         #
            #         # })
            #
            #
            # # print(count_request)
            # # print(self.from_date,self.to_date)
            # # print(datetime.now())
            # # print(self.emp_check_out.date())
            # # if count_request > 2:
            # #     self.env['hr.leave'].create({
            # #         'employee_id': self.name.id,
            # #         'date_from':self.emp_check_in ,
            # #         'date_to': self.emp_check_in,
            # #         'holiday_status_id': 1,
            # #         'number_of_days': 1,
            # #         'name': 'Attendance Request',
            # #
            # #     })
            # #
            #

            search_attendance = self.env['hr.attendance']
            print("here boi")
            adjusted_check_in = datetime.strftime(self.emp_check_in, '%Y-%m-%d')
            print('My',adjusted_check_in)
            search_record = search_attendance.search(
                [('employee_id', '=', self.name.id),('attend_check_in','=',adjusted_check_in)])
            print('My search record', search_record)
            if not search_record:
                print('My create')
                self.env['hr.attendance'].create({
                    'employee_id':self.name.id,
                    'check_in': self.emp_check_in,
                    'check_out': self.emp_check_out,

                })
            else:
                print('My write')
                search_record.write({
                    'check_in': self.emp_check_in,
                    'check_out': self.emp_check_out,

                })
            return self.write({'state': 'done'})
