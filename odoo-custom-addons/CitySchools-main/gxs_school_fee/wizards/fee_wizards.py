from odoo import models, fields, api
from datetime import datetime,date
class GenerateMonthlyInvoicesWizard(models.TransientModel):
    _name = 'generate.monthly.invoices.wizard'
    _description = 'Generate Monthly Invoices Wizard'

    @api.model
    def action_is_student(self):
        print('[[[[[[[]]]]]')
        docs = self.env['op.student'].browse(self.env.context.get('active_id'))
        if docs:
            return True
        else:
            return False

    @api.model
    def action_get_class(self):
        docs = self.env['op.student'].search([('id','=',self.env.context.get('active_id'))])
        return docs.year_id.ids

    @api.model
    def action_get_student(self):
        docs = self.env['op.student'].search([('id', '=', self.env.context.get('active_id'))])
        return docs.ids


    @api.model
    def action_get_invoice_history(self):
        docs = self.env['op.student'].search([('id', '=', self.env.context.get('active_id'))])
        moves = self.env['account.move'].search([('student_id','=',docs.id)])
        print(moves)
        return moves.ids

    classes = fields.Many2many('op.academic.year', string='Class', store=True, copy=True,default= action_get_class)
    date = fields.Date('Date', store=True, copy=False, default=fields.Date.context_today)
    student_ids = fields.Many2many('op.student', string='Students',domain="[('year_id','in',classes)]",default= action_get_student)
    admission_fee = fields.Boolean(string="Admission Fee")
    annual_charges = fields.Boolean(string="Annual Charges")
    security_charges = fields.Boolean(string="Security Charges")
    registration_fee = fields.Boolean(string="Registration Fee")
    fee_arrears = fields.Boolean(string="Fee Arrears")

    is_from_student = fields.Boolean(string='Is From student',default= action_is_student)


    invoice_history = fields.Many2many('account.move',string="Invoice History",default= action_get_invoice_history)

    month_selection = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string='Select Month')

    first_day_of_month = fields.Date(string='First Day of Month', compute='_compute_first_day_of_month')

    @api.depends('month_selection', 'date')
    @api.constrains('month_selection')
    def _compute_first_day_of_month(self):
        print('ttttttttt')
        for record in self:
            if record.month_selection:
                if record.date:
                    date = datetime.strptime(f'{record.date.year}-{record.month_selection}-01', '%Y-%m-%d')
                    record.first_day_of_month = date.date()
                    record.date = date.date()
                else:
                    current_year = datetime.today().year  # Get the current year
                    first_date = datetime.strptime(f'{current_year}-{record.month_selection}-01', '%Y-%m-%d')
                    record.first_day_of_month = first_date.date()
                    record.date = first_date.date()
            else:
                record.first_day_of_month = False
                record.date = False

    def generate_invoices(self):
        list_ids = []
        if self.student_ids:
            for student in self.student_ids:
                id = self.env['fee.structure'].create_invoice(self.classes,student,self.date,self)
                list_ids = list_ids + id
        elif self.classes:
            students = self.env['op.student'].search([('year_id', '=', self.classes.ids)])
            for student in students:
                id = self.env['fee.structure'].create_invoice(self.classes, student, self.date, self)
                list_ids = list_ids + id
        else:
            class_ids =  self.env['op.academic.year'].search([])
            students = self.env['op.student'].search([('year_id','=',class_ids.ids)])
            for student in students:
                id = self.env['fee.structure'].create_invoice(self.classes,student,self.date,self)
                list_ids = list_ids + id

        print(list_ids,'ddddddd[e')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fee Voucher',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', list_ids)],

        }


