from odoo import models, fields


class StudentHallTicket(models.TransientModel):
    """ Student Hall Ticket Wizard """
    _name = "student.hall.ticket"
    _description = "Student Hall Ticket"

    exam_session_id = fields.Many2one(
        'op.exam.session', 'Exam Session', required=True,
        domain=[('state', 'not in', ['draft', 'cancel', 'done'])])

    def print_report(self):
        data = self.read(['exam_session_id'])[0]
        return self.env.ref(
            'gxs_exam.action_student_hall_ticket_report') \
            .report_action(self, data=data)
