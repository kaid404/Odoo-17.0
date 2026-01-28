from odoo import models
import calendar

class SalarySheetXlsx(models.AbstractModel):
    _name = 'report.salary_xlsx_report.salary_sheet_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Salary Sheet')

        col_widths = {}

        def write_cell(row, col, value, fmt):
            sheet.write(row, col, value, fmt)
            value = str(value) if value else ''
            col_widths[col] = max(col_widths.get(col, 0), len(value))

        title_fmt = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })

        header_fmt = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center'
        })

        text_fmt = workbook.add_format({
            'border': 1
        })

        number_fmt = workbook.add_format({
            'border': 1,
            'align': 'right'
        })
        total_fmt = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right'
        })

        fixed_headers = [
            'Sr#',
            'Employee Code',
            'Name',
            'CNIC',
            'DOJ',
            'Bank',
            'Designation',
            'Grade',
            'Team',
            'Worked Days',
        ]
        salary_headers = [
            ('BASIC', 'Salary'),
            ('INC', 'Increment'),
            ('GROSS', 'Gross Salary'),
            ('MBMA', 'Mobile/Medical Allowance'),
            ('FD', 'Food Allowance'),
            ('OPD', 'OPD Re-imbursement'),
            ('GROSS_ALL', 'Gross Salary With Allowances'),
            ('AR', 'Arrears'),
            ('OT', 'Overtime'),
            ('GROSS_ARR', 'Gross Salary+Arrears'),
            ('LATE_CNT', 'Total Lates'),
            ('ABS_CNT', 'Total Absents'),
            ('LATEDED', 'Late Deductions'),
            ('AB', 'Absent Deductions'),
            ('ATT_DED', 'Total Attendance Deductions'),
            ('OD', 'Other Deductions'),
            ('EOBIE', 'EOBI Deductions'),
            ('CAR', 'Car/Loan Return'),
            ('PF', 'PF Deduction'),
            ('TAJ', 'Tax'),
            ('TOT_DED', 'New Total Deductions'),
            ('NET', 'Net Salary'),
        ]

        payslips = self.env['hr.payslip'].browse(data.get('payslips'))

        if wizard.date_from:
            month_name = calendar.month_name[wizard.date_from.month]
            year = wizard.date_from.year
        else:
            month_name = ''
            year = ''

        title = f"Admin Staff Salary Sheet for the Month of {month_name}-{year}"
        total_columns = len(fixed_headers) + len(salary_headers)

        sheet.merge_range(0, 0, 1, total_columns - 1, title, title_fmt)

        row = 2
        col = 0
        for h in fixed_headers:
            write_cell(row, col, h, header_fmt)
            col += 1

        rule_col_index = {}
        for code, label in salary_headers:
            write_cell(row, col, label, header_fmt)
            rule_col_index[code] = col
            col += 1

        sr = 1
        row = 3
        rule_totals = {code: 0.0 for code, label in salary_headers}

        for payslip in payslips:
            emp = payslip.employee_id
            contract = payslip.contract_id

            month_cal = calendar.monthcalendar(wizard.date_from.year, wizard.date_from.month)
            sundays = sum(1 for week in month_cal if week[calendar.SUNDAY] != 0)

            paid_leaves = self.env['hr.leave'].search([
                ('employee_id', '=', emp.id),
                ('state', '=', 'validate'),
                ('holiday_status_id.name', '=', 'Unpaid'),
                ('request_date_from', '<=', wizard.date_to),
                ('request_date_to', '>=', wizard.date_from),
            ])

            paid_leave_days = sum(paid_leaves.mapped('number_of_days'))

            no_of_work_days = payslip.attendance_count + sundays + paid_leave_days



            write_cell(row, 0, sr, number_fmt)
            write_cell(row, 1, emp.barcode or '', text_fmt)
            write_cell(row, 2, emp.name or '', text_fmt)
            write_cell(row, 3, emp.identification_id or '', text_fmt)
            write_cell(
                row, 4,
                contract.date_start.strftime('%d-%m-%Y') if contract.date_start else '',
                text_fmt
            )
            write_cell(row, 5, emp.bank_account_id.acc_number if emp.bank_account_id else '', text_fmt)
            write_cell(row, 6, emp.job_id.name or '', text_fmt)
            write_cell(row, 7, contract.opd_grade or '', text_fmt)
            write_cell(row, 8, emp.x_studio_team.x_name or '', text_fmt)
            write_cell(row, 9, no_of_work_days, number_fmt)

            rule_amounts = {line.code: line.total for line in payslip.line_ids}
            computed_values = {}

            for code, col_idx in rule_col_index.items():
                if code == 'LATE_CNT':
                    late_days = self.env['late.deduction.lines'].search_count([
                        ('employee_id', '=', emp.id),
                        ('check_in', '>=', wizard.date_from),
                        ('check_out', '<=', wizard.date_to),
                        ('exemption', '=', False),
                    ])

                    amount = late_days

                elif code == 'INC':
                    increment_amount = 0.0
                    if contract:
                        for inc in contract.increment_detail_ids:
                            if inc.date and inc.date >= wizard.date_from and inc.date <= wizard.date_to:
                                print(inc.wage)
                                increment_amount += inc.amount

                    amount = increment_amount

                elif code == 'ABS_CNT':
                    absent_days = self.env['absent.deduction.lines'].search_count([
                        ('employee_id', '=', emp.id),
                        ('absent_date', '>=', wizard.date_from),
                        ('absent_date', '<=', wizard.date_to),
                    ])
                    amount = absent_days

                elif code == 'GROSS_ALL':
                    amount = sum(rule_amounts.get(c, 0.0) for c in ['GROSS', 'MB','MA', 'FD', 'OPD'])
                    computed_values['GROSS_ALL'] = amount
                elif code == 'MBMA':
                    amount = sum(rule_amounts.get(c, 0.0) for c in ['MB','MA'])
                    computed_values['GROSS_ALL'] = amount

                elif code == 'GROSS_ARR':
                    amount = (
                            computed_values.get('GROSS_ALL', 0.0)
                            + rule_amounts.get('AR', 0.0)
                            + rule_amounts.get('OT', 0.0)
                    )

                elif code == 'ATT_DED':
                    amount = (
                            rule_amounts.get('LATEDED', 0.0)
                            + rule_amounts.get('AB', 0.0)
                    )
                    computed_values['ATT_DED'] = amount

                elif code == 'TOT_DED':
                    amount = (
                            computed_values.get('ATT_DED', 0.0)
                            + sum(rule_amounts.get(c, 0.0) for c in ['OD', 'EOBIE', 'CAR', 'PF', 'TAJ'])
                    )

                else:
                    amount = rule_amounts.get(code, 0.0)
                # amount = rule_amounts.get(code, 0.0)
                sheet.write(row, col_idx, amount, number_fmt)
                rule_totals[code] += amount

            sr += 1
            row += 1

        sheet.merge_range(row, 0, row, 9, 'TOTAL', total_fmt)
        for code, col_idx in rule_col_index.items():
            write_cell(row, col_idx, rule_totals.get(code, 0.0), total_fmt)

        for col, width in col_widths.items():
            sheet.set_column(col, col, min(width + 2, 40))
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 18)
        sheet.set_column('E:E', 18)
        sheet.set_column('F:F', 22)
