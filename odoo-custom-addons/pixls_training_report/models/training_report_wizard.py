from odoo import models, fields


class TrainingReportWizard(models.TransientModel):
    _name = "pixls.training.report.wizard"
    _description = "Training Report Wizard"

    program_ids = fields.Many2many("training.program", string="Training Programs")
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)

    def print_report(self):
        date_from = self.date_from
        date_to = self.date_to

        domain = [
            ('start_date', '>=', date_from),
            ('end_date', '<=', date_to),
        ]
        if self.program_ids:
            domain.append(('training_program', 'in', self.program_ids.ids))

        programs = self.env['pixls.training.program'].search(domain)

        result_data = {}

        for program in programs:
            students = program.students

            if not students:
                continue

            assignment_lines = self.env['assignment.training.student.result.line'].search([
                ('assignement_result_id.training_program_id', '=', program.id)])

            jury_lines = self.env['jury.trainer.result.line'].search([
                ('jury_result_id.training_program_id', '=', program.id),
            ])

            for line in assignment_lines:
                student_id = line.student_id.id

                if student_id not in result_data:
                    result_data[student_id] = {
                        'student_name': line.student_id.name,
                        'assignment_total': 0.0,
                        'assignment_obt_total': 0.0,
                        'assignment_weightage': 0.0,
                        'assignment_remarks': '',
                        # 'assignment_marks': [],
                        'jury_marks': []
                    }

                result_data[student_id]['assignment_total'] += line.total or 0.0
                result_data[student_id]['assignment_obt_total'] += line.obt_total or 0.0

                # result_data[student_id]['assignment_marks'].append({
                #     'trainer_name': line.assignement_result_id.trainer.name,
                #     'total': line.total,
                #     'obt_total': line.obt_total,
                #     'remarks': line.remarks,
                # })

            for line in jury_lines:
                student_id = line.student_id.id

                if student_id not in result_data:
                    result_data[student_id] = {
                        'student_name': line.student_id.name,
                        'assignment_total': 0.0,
                        'assignment_obt_total': 0.0,
                        'remarks': '',
                        # 'assignment_marks': [],
                        'jury_marks': []
                    }

                result_data[student_id]['jury_marks'].append({
                    'jury_name': line.jury_result_id.jury.name,
                    'total': line.total,
                    'obt_total': line.obt_total,
                    'remarks': line.remarks,
                })

        final_report_data = {
            'programs': result_data
        }

        return self.env.ref("pixls_training_report.action_training_report").report_action(self, data=final_report_data)
