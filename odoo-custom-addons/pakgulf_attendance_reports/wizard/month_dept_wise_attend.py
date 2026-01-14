import time
import math
import logging
from datetime import date
import calendar
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
from io import StringIO
import io
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

import pytz
from odoo import models, fields, api
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from datetime import date as delta1
from datetime import datetime
    

class PakEmployeeAttendanceReport(models.TransientModel):
    _name = 'pakgulf.emp.wise.attendance'
    _description = "Attendance Report Wizard"

    company_id = fields.Many2one('res.company',string="Employee Company")
    employee_ids = fields.Many2many('hr.employee',string="Employee Name")
    department_ids = fields.Many2many('hr.department',string="Departments")
    from_date = fields.Date('From Date ', default=lambda self: fields.Date.to_string(delta1.today()), required=True)
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    date = fields.Date(string='Date',default=date.today())

    def print_emp_attendance(self ,mode='date'):
        date = [] 
        day = [] 
        datas = []
        employee = []
        reporting = []
        new_format = "%H:%M"
        dep_data = []
        dep_list = []
        domain = [('emp_company_id', '=', self.company_id.id)]
        if self.employee_ids:
            domain.append(('id', 'in', self.employee_ids.ids))
        if self.company_id:
            domain.append(('emp_company_id', 'in', self.company_id.id))
        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))
            department_ids = self.department_ids

        else:
            department_ids = self.env["hr.employee"].search(domain).mapped('department_id')
            domain.append(('department_id', 'in', department_ids.ids))

        planning_record_test = self.env["hr.employee"].search(domain)
        
        date_t = fields.Date.from_string(self.to_date)
        date_fro = fields.Date.from_string(self.from_date)
        rest_day = date_t - date_fro
        days = []
        dateelis = []

        for d in range(0, rest_day.days + 1):
            rest_days = d + 1
            datee = date_fro + timedelta(days=d)
            dateelis.append({'datee': datee, 'atte': ''})
            days.append({
                'rest_days': rest_days,
                'datee': datee,
                'atte': '',
            })
        total_working_days = 0
        for dep in department_ids:
            domain = [('emp_company_id', '=', self.company_id.id)]

            if self.employee_ids:
                domain.append(('id', 'in', self.employee_ids.ids))
            
            domain.append(('department_id', '=', dep.id))
            planning_record_test = self.env['hr.employee'].search(domain)
            if planning_record_test:
                dep_list.append(dep.name)
            datas = []
            for emp in planning_record_test:
                total_working_days = 0.0
                day_work_hor = 0.0
                days=[]
                dateelis=[]
                rest_days = 0
                for d in range(0, rest_day.days + 1):
                    rest_days = d + 1
                    datee = date_fro + timedelta(days=d)
                    dateelis.append({'datee': datee, 'atte': ''})
                    days.append({
                        'rest_days': rest_days,
                        'datee': datee,
                        'atte': '',
                    })
                karachi_timezone = timezone("Asia/Karachi")

                for date in days:
                    atendance = self.env['hr.attendance'].search(
                        [('employee_id', '=', emp.id), ('checkin_date', '=', date['datee'])])
                    date['atte'] = ''
                    checkin = ''
                    checkout = ''
                    late_policy = self.env['gxs.late.policy.dep'].search([
                        ('department_ids', 'in', dep.id),
                        ('date_from', '<=', date['datee']),
                        ('date_to', '>=', date['datee'])
                    ])
                    if atendance.late_emp > late_policy.time:
                        date['atte'] = 'PL'
                        total_working_days += 1
                        day_work_hor += atendance.worked_hours
                        checkin = atendance.check_in.astimezone(karachi_timezone).strftime(new_format) if atendance.check_in else ''
                        checkout = atendance.check_out.astimezone(karachi_timezone).strftime(new_format) if atendance.check_out else ''

                        if atendance.check_in:
                            checkin = atendance.check_in.astimezone(karachi_timezone).strftime(new_format)
                        if atendance.check_out:
                            checkout = atendance.check_out.astimezone(karachi_timezone).strftime(new_format)
                    elif atendance:
                        date['atte'] = 'PP'
                        total_working_days += 1
                        day_work_hor += atendance.worked_hours
                        checkin = atendance.check_in.astimezone(karachi_timezone).strftime(new_format) if atendance.check_in else ''
                        checkout = atendance.check_out.astimezone(karachi_timezone).strftime(new_format) if atendance.check_out else ''
                        if atendance.check_in:
                            checkin = atendance.check_in.astimezone(karachi_timezone).strftime(new_format)
                        if atendance.check_out:
                            checkout = atendance.check_out.astimezone(karachi_timezone).strftime(new_format)               
                    else:
                        
                        if date['datee'].weekday() == 6:
                            date['atte'] = 'WE'
                            total_working_days += 1
                        else:
                            # Check if the working schedule is not defined for the day in the shift
                            working_schedule = emp.resource_calendar_id.attendance_ids.filtered(lambda a: a.dayofweek == str(date['datee'].weekday()))
                            if not working_schedule:
                                date['atte'] = '-'
                            else:
                                leave = self.env["hr.leave"].search(
                                    [('employee_id', '=', emp.id), ('state', '=', 'validate'),
                                     ('request_date_from', '<=', date['datee']),
                                     ('request_date_to', '>=', date['datee'])], limit=1)
                                if leave:
                                    # Check if the leave is associated with a work entry type
                                    if leave.holiday_status_id.work_entry_type_id:
                                        date['atte'] = leave.holiday_status_id.work_entry_type_id.code
                                        total_working_days += 1
                                    else:
                                        date['atte'] = 'AB'  # Default code for other leaves
                                        total_working_days += 1
                                else:
                                    date['atte'] = 'AB'
                                day_work_hor += atendance.worked_hours


                    date['checkin'] = checkin
                    date['checkout'] = checkout
                    
                plan = self.env['hr.contract.history'].search([('employee_id', '=', emp.id)])
                      
                eng_date = ''
                for contr in plan.contract_ids:
                    
                    eng_date = contr.date_start
                    
                datas.append({
                    'code': emp.barcode,
                    'name': emp.name,
                    'job_id': emp.job_id.name,
                    'department_id': emp.department_id.name,
                    'shift': emp.resource_calendar_id.name,
                    'eng_date': eng_date,
                    'work_hor': day_work_hor,
                    'total_working_days': total_working_days,
                    'checkin': checkin,
                    'checkout': checkout,
                    'days': days,

                })
            dep_data.append({
                'dep_name': dep.name,
                'datas': datas,
                })

        res = {
            'employee_rec': employee,
            'dep_data': dep_data,
            'reporting': reporting,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'days': days,
        }
        data = {
            'form': res,
        }
        return self.env.ref('pakgulf_attendance_reports.pakgulf_monthly_emp_wise_report').report_action([], data=data)






    def attendance_xlsx(self):
        print("Pakistan Zindabad-----------------------------------")
        return self.env.ref('pakgulf_attendance_reports.pakgulf_monthly_emp_wise_xlsx').report_action(self)

class HrAttendanceOvertime(models.Model):
    _inherit = "hr.attendance.overtime"
    _description = "Attendance Overtime"

