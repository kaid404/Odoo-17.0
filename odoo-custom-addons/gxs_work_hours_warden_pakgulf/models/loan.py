from odoo import models, fields, api
from datetime import datetime, time, timedelta,date
from odoo.exceptions import UserError, ValidationError, MissingError
class kaytasLoan(models.Model):
    _name = 'loan.loan'
    state = fields.Selection([

        ('draft','Draft'),
        ('approved','Approved'),
        ],required=True,default='draft',tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    from_request_date = fields.Date('Request Date')
    request_date = fields.Date('From Date', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    description = fields.Char(string='Description')
    loan_apply = fields.Float(string='Apply Loan')
    max_loan = fields.Float(string='Max Loan can apply', compute='_overtime_emp_hour_count', store=True)
    attrs_condition = fields.Boolean(string='con')

    @api.onchange('loan_apply')
    def loan_limt(self):
        if self.loan_apply:
            if self.loan_apply <= self.max_loan:
                pass
            else:
                 self.loan_apply = 0
                 
    
    @api.onchange('request_date','employee_id')
    def _overtime_emp_hour_count(self):
        self.max_loan
        self.attrs_condition = False

        today = date.today()
        print(today,self.request_date)
        date_half = today - self.request_date
        print(date_half)
        date_half = date_half.total_seconds() / 3600.0
        date_half = date_half / 24
        print(date_half)

        # date_half =  self.request_date - loan_date[0].request_date
        # print(date_half)
        # date_half = date_half.total_seconds() / 3600.0
        # date_half = date_half/24
        # print(date_half)
        if self.request_date and self.employee_id and date_half > 13:
            self.from_request_date = today
            print('lllll', date_half)
            wage = self.env["hr.contract"].search(
                [('employee_id', '=', self.employee_id.id)
                 ])
            print(wage)
            self.max_loan = wage[0].wage / 2
            self.attrs_condition = True
        elif self.request_date and self.employee_id and date_half > 15:
            pass
            # raise ValidationError(f"At this {today} date the  {self.employee_id.name} is not eligible for advance")
        else:
            pass



        # self.max_loan
        # self.attrs_condition = False
        # if self.request_date and self.employee_id:
        #     loan_date = self.env["loan.loan"].search(
        #         [('employee_id', '=', self.employee_id.id)
        #          ])
        #     if loan_date:
        #         print(loan_date)
        #         today = date.today()
        #         date_half =  today - self.request_date
        #         print(date_half)
        #         date_half = date_half.total_seconds() / 3600.0
        #         date_half = date_half/24
        #         print(date_half)
        #
        #         # date_half =  self.request_date - loan_date[0].request_date
        #         # print(date_half)
        #         # date_half = date_half.total_seconds() / 3600.0
        #         # date_half = date_half/24
        #         # print(date_half)
        #         if self.request_date and self.employee_id and date_half >= 15:
        #
        #             print('lllll',date_half)
        #             wage = self.env["hr.contract"].search(
        #                 [('employee_id', '=', self.employee_id.id)
        #                   ])
        #             print(wage)
        #             self.max_loan = wage[0].wage/2
        #             self.attrs_condition = True
        #         else:
        #             pass
        #     else:
        #         wage = self.env["hr.contract"].search(
        #             [('employee_id', '=', self.employee_id.id)
        #              ])
        #         print(wage)
        #         self.max_loan = wage[0].wage / 2
        #         self.attrs_condition = True
    def approve(self):
        if self.loan_apply == 0.0:
            raise ValidationError(f"Amount is not eligible for advance")
        self.state = 'approved'

        # attendance = self.env["hr.attendance"].search(
        #     [('employee_id', '=', self.employee_id.id),
        #      ('checkin_date', '=', self.request_date)])
        # attendance.write({'assumption_request': 'Request Approved'
        #                   })

    def unlink(self):

        if self.state == 'draft':
            return super(kaytasLoan, self).unlink()
        else:
            raise ValidationError(('Not deletable on Approved stage'))


class kaytasLoanlone(models.Model):
    _name = 'loan.loan.loan'
    state = fields.Selection([

        ('draft', 'Draft'),
        ('approved', 'Approved'),
    ], required=True, default='draft', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    loan_type = fields.Char('loan Type')
    request_date = fields.Date('Request Date')
    description = fields.Char(string='Description')
    loan_apply = fields.Float(string='Apply Loan')
    max_loan = fields.Float(string='Max Loan can apply', compute='_overtime_emp_hour_count', store=True)
    attrs_condition = fields.Boolean(string='con')

    @api.onchange('loan_apply')
    def loan_limt(self):
        if self.loan_apply:
            if self.loan_apply <= self.max_loan:
                pass
            else:
                self.loan_apply = 0

    @api.onchange('request_date', 'employee_id')
    def _overtime_emp_hour_count(self):
        # import requests
        # import json
        # response_API = requests.get('https://gmail.googleapis.com/$discovery/rest?version=v1')
        # # print(response_API.status_code)
        # data = response_API.text
        # parse_json = json.loads(data)
        # # print(parse_json)
        # info = parse_json['description']
        # print("Info about API:\n", info)
        # key = parse_json['parameters']['key']['description']
        # print("\nDescription about the key:\n", key)

        print('_______________________________________________')
        import requests
        import json
        response_API = requests.get('https://api.covid19india.org/state_district_wise.json')
        # print(response_API.status_code)
        data = response_API.text
        parse_json = json.loads(data)
        print(len(parse_json))
        for i in parse_json:
            print(i)
        # print(parse_json)
        # active_case = parse_json['Andaman and Nicobar Islands']['districtData']['South Andaman']['active']
        # print("Active cases in South Andaman:", active_case)


        self.max_loan
        self.attrs_condition = False
        if self.request_date and self.employee_id:
            permanent = self.env["hr.contract"].search(
                [('employee_id', '=', self.employee_id.id)
                 ])

            if not permanent:
                raise ValidationError(f"{self.employee_id.name} is not permanent only permanent employee can apply for loan")

            loan_date = self.env["loan.loan.loan"].search(
                [('employee_id', '=', self.employee_id.id)
                 ])
            if loan_date:
                print(loan_date)

                date_half =  self.request_date - loan_date[0].request_date
                print(date_half)
                date_half = date_half.total_seconds() / 3600.0
                date_half = date_half/24
                print(date_half)
                if self.request_date and self.employee_id and date_half >= 15:

                    print('lllll',date_half)
                    wage = self.env["hr.contract"].search(
                        [('employee_id', '=', self.employee_id.id)
                          ])
                    print(wage)
                    self.max_loan = wage[0].wage/2
                    self.attrs_condition = True
                elif self.request_date and self.employee_id and date_half > 15:
                    pass
                    # raise ValidationError(
                    #     f"At this {self.request_date} date the  {self.employee_id.name} is not eligible for loan")
                else:
                    pass
            else:
                wage = self.env["hr.contract"].search(
                    [('employee_id', '=', self.employee_id.id)
                     ])
                print(wage)
                self.max_loan = wage[0].wage / 2
                self.attrs_condition = True

    def approve(self):
        if self.loan_apply == 0.0:
            raise ValidationError(f"Amount is not eligible for advance")
        self.state = 'approved'

        # attendance = self.env["hr.attendance"].search(
        #     [('employee_id', '=', self.employee_id.id),
        #      ('checkin_date', '=', self.request_date)])
        # attendance.write({'assumption_request': 'Request Approved'
        #                   })

    def unlink(self):

        if self.state == 'draft':
            return super(kaytasLoanloan, self).unlink()
        else:
            raise ValidationError(('Not deletable on Approved stage'))
