from odoo import models, fields

class FacultyDiary(models.Model):
    _name = 'faculty.diary'
    _description = 'Faculty Diary'

    name = fields.Char(string="Diary Name", required=True)
    diary_line_ids = fields.One2many('faculty.diary.line', 'diary_id', string="Diary Entries")
    date = fields.Date(string="Date", required=False)


class FacultyDiaryLine(models.Model):
    _name = 'faculty.diary.line'
    _description = 'Faculty Diary Line'

    subject = fields.Char(string="Subject", required=True)
    class_id = fields.Char(string="Class", required=True)
    date = fields.Date(string="Date", required=False)
    description = fields.Text(string="Description", required=True)
    diary_id = fields.Many2one('faculty.diary', string="Diary")
