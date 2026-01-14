import pdb
import time
from datetime import datetime, date, timedelta
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.osv import expression

date_format = '%Y-%m-%d'
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OdooCMSGenerateAttendanceRoaster(models.TransientModel):
    _name = 'odoocms.generate.attendance.roaster'
    _description = 'Generate Attendance Roaster'

    date_class = fields.Date('Class Date From', default=lambda self: fields.Date.today())
    date_class_to = fields.Date('Class Date To', default=lambda self: fields.Date.today())

    section_ids = fields.Many2many('class.section', string='Section')


    def generate_roaster(self):
        date_list = []
        date_from = self.date_class
        date_to = self.date_class_to
        # print(self.to_date, self.from_date)
        date1 = fields.Date.from_string(date_from)
        date2 = fields.Date.from_string(date_to)

        delta = date2 - date1

        valid_weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        for n1 in range(delta.days + 1):
            res = date1 + timedelta(days=n1)
            if res.strftime('%A') in valid_weekdays:
                date_list.append(res)


        for rec in self.section_ids:
            att_register = self.env['op.attendance.register'].sudo().search([('section_id','=',rec.id)])
            if not att_register:
                course_id = self.env['op.course'].sudo().search([('class_id', '=', rec.class_id.id)])

                att_register = self.env['op.attendance.register'].sudo().create({'course_id':course_id.id,'name':f"{rec.name}-{rec.class_id.name}-{self.date_class.year}",'code':f"{rec.name}-{rec.class_id.name}-{self.date_class.year}",'section_id':rec.id})
            for d in date_list:
                sheet_id = self.env['op.attendance.sheet'].sudo().search([('register_id', '=', att_register.id),('attendance_date','=',d)])
                if not sheet_id:
                    sheet_id = self.env['op.attendance.sheet'].sudo().create(
                        {'register_id': att_register.id, 'attendance_date': d, 'name': att_register.name,
                         'faculty_id': rec.faculty.id, 'section_name': rec.name, 'class_name': rec.class_id.id,
                         'year': rec.year_id.id})
                for std in rec.students:
                    self.env['op.attendance.line'].create({'student_id':std.id,'register_id':att_register.id,'attendance_id':sheet_id.id})


class ClassSection(models.Model):
    _inherit = 'class.section'

    faculty_id = fields.Many2one('op.faculty', string='Faculty Name')


