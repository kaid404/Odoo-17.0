from reportlab.lib.validators import isNoneOrInt

from odoo import models, fields, api

class ActiveStudentList(models.TransientModel):

    _name = 'active.student.list'
    _description = 'Fee Balance List for City School'

    student_id = fields.Many2one('op.student')
    st_class = fields.Many2one('op.academic.year', string="Class")
    section = fields.Many2one('class.section', string="Section")
    campus = fields.Many2one('res.company', string="Campus")

    def print_student_list(self):
        st_class = self.st_class
        section = self.section
        campus = self.campus

        domain = []

        class_order = {
            "Pre-Nursery": 0, "Nursery": 1, "Prep": 2, "Class-I": 3, "Class-II": 4,
            "Class-III": 5, "Class-IV": 6, "Class-V": 7, "Class-VI": 8, "Class-VII": 9,
            "Class-VIII": 10, "Class-IX": 11, "Class-X": 12
        }

        students_data = {}

        if self.st_class:
            domain.append(('year_id', '=', st_class.id))

        if self.section:
            domain.append(('section_id', '=', section.id))

        if self.campus:
            domain.append(('company_id', '=', campus.id))

        all_students = self.env['op.student'].search(domain)


        for student in all_students:
            class_section = f'{student.year_id.name} - {student.section_id.name}'

            if class_section not in students_data:
                students_data[class_section] = []

            if student.state == 'admitted':
                students_data[class_section].append({
                    'roll_number': student.gr_no,
                    'adm#': 'N/A',
                    'adm_date': student.create_date.date().strftime('%d %B %Y'),
                    'name': f"{student.first_name} {student.middle_name if student.middle_name else ''} {student.last_name}",
                    'father_name': student.father_name if student.father_name else 'N/A',
                    'dob': student.birth_date,
                    'mob': student.mobile,
                })


        filtered_data = {k: v for k, v in students_data.items() if v}
        #
        sorted_students_data = dict(
            sorted(filtered_data.items(), key=lambda item: class_order.get(item[0].split(" - ")[0], 99))
        )



        final_report_data = {
            'company_logo': f"data:image/png;base64,{self.env.company.logo.decode('utf-8')}" if self.env.company.logo else None,
            'company_name': ', '.join(campus.mapped('name')) if campus else self.env.company.name,
            'st_data': sorted_students_data,
        }


        return self.env.ref('active_student_list.active_student_action_report').report_action(self, data=final_report_data)

