from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class GlobalInputs(models.Model):
    _name = 'global.input'
    _description = 'Global Input'

    name = fields.Char('Name', store=True)
    date_to = fields.Date(string='Date To',required=True)
    date_from = fields.Date(string='Date From',required=True)
    apply_by = fields.Selection([
        ('batch', "Batch"),
        ('dpt', "Department"),
        ('comp', "Company"),
        ('emp', "Employees"),
    ], string="Apply Inputs By", default='batch')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'), ], )
    batch_id = fields.Many2one('hr.payslip.run', 'Batch')
    department_id = fields.Many2one('hr.department', 'Department')
    company_id = fields.Many2one('res.company', 'Company')
    is_emp = fields.Boolean('By Employee',compute='set_emp',store=True)
    input_line_ids = fields.One2many(
        'global.input.line', 'input_id', string='Payslip Inputs', store=True,
        readonly=False)

    def set_draft(self):
        self.write({'state':'draft'})

    @api.depends('apply_by')
    def set_emp(self):
        if self.apply_by == 'emp':
            self.is_emp = True
        else:
            self.is_emp = False


    @api.onchange('apply_by')
    def onchangeapply(self):
        # self.employee = None
        self.company_id = None
        self.batch_id = None
        self.department_id = None

    def add_inputs(self):
        list = []
        input_list = {}
        if self.batch_id:
            batch_payslip = self.env['hr.payslip'].search(
                [('payslip_run_id', '=', self.batch_id.id),('date_to', '<=', self.date_to),
                                                 ('date_from', '>=', self.date_from),
                 ('state', 'not in', ['done', 'refuse', 'paid'])])
            print(batch_payslip)
            for rec in self.input_line_ids:
                input_list = \
                    (0, 0, {
                        "name": rec.name,
                        "input_type_id": rec.input_type_id.id,
                        "sequence": rec.sequence,
                        "code": rec.code,
                        "amount": rec.amount

                    })
                list.append(input_list)
            print(list)
            for slips in batch_payslip:
                print(slips)
                slips.write({"input_line_ids": list})
                slips.compute_sheet()
            self.state = 'done'

        elif self.company_id:
            cop_payslip = self.env['hr.payslip'].search(
                [('company_id', '=', self.company_id.id), ('state', '=', 'verify')])
            for rec in self.input_line_ids:
                input_list = \
                    (0, 0, {
                        "name": rec.name,
                        "input_type_id": rec.input_type_id.id,
                        "sequence": rec.sequence,
                        "code": rec.code,
                        "amount": rec.amount

                    })
                list.append(input_list)
            print(list)
            for slips in cop_payslip:
                print(slips)
                slips.write({"input_line_ids": list})
                slips.compute_sheet()
            self.state = 'done'


        elif self.department_id:
            dep_payslip = self.env['hr.payslip'].search(
                [('department_id', '=', self.contract_id.department_id.id), ('state', '=', 'verify')])
            for rec in self.input_line_ids:
                input_list = \
                    (0, 0, {
                        "name": rec.name,
                        "input_type_id": rec.input_type_id.id,
                        "sequence": rec.sequence,
                        "code": rec.code,
                        "amount": rec.amount

                    })
                list.append(input_list)
            print(list)
            for slips in dep_payslip:
                print(slips)
                slips.write({"input_line_ids": list})
                slips.compute_sheet()
            self.state = 'done'

        elif self.apply_by == 'emp':
            for rec in self.input_line_ids:
                emp_payslip = self.env['hr.payslip'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'verify')])
                my_list = []
                print(emp_payslip)
                if emp_payslip:
                    input_list = \
                        (0, 0, {
                            "name": rec.name,
                            "input_type_id": rec.input_type_id.id,
                            "sequence": rec.sequence,
                            "code": rec.code,
                            "amount": rec.amount

                        })
                    my_list.append(input_list)
                    for slip in emp_payslip:
                        slip.write({"input_line_ids": my_list})
                        slip.compute_sheet()
                else:
                    continue
            self.state = 'done'

        else:
            raise ValidationError(_('Unable to find any payslip to perform action on.'))

    def name_get(self):
        """
        name_get that supports displaying location name and model as prefix
        """
        result = []
        for rec in self:
            if rec.company_id == 1:
                if rec.customer_rank > 0 or rec.supplier_rank > 0:
                    # result.append((rec.id , + rec.product_category_code))
                    name = "%s - %s" % (rec.product_category_code, rec.name)
                    result.append((rec.id, name))
                else:
                    name = "%s" % (rec.name)
                    result.append((rec.id, name))
            else:
                name = "%s" % (rec.name)
                result.append((rec.id, name))
        print(result)
        return result


class GlobalInputLine(models.Model):
    _name = 'global.input.line'

    name = fields.Char(string="Description")
    input_id = fields.Many2one('global.input', string='Global Input', ondelete='cascade', index=True)
    sequence = fields.Integer(required=True, index=True, default=10)
    input_type_id = fields.Many2one('hr.payslip.input.type', string='Type', required=True, )
    # _allowed_input_type_ids = fields.Many2many('hr.payslip.input.type',
    #                                            related='payslip_id.struct_id.input_line_type_ids')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    code = fields.Char(related='input_type_id.code', required=True,
                       help="The code that can be used in the salary rules")

    amount = fields.Float(
        string="Count",
        help="It is used in computation. E.g. a rule for salesmen having 1%% commission of basic salary per product can defined in expression like: result = inputs.SALEURO.amount * contract.wage * 0.01.")
