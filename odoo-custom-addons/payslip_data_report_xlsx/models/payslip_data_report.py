from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


class PayslipDataReportXlsx(models.Model):
    _name = 'report.payslip_data_report_xlsx.payslip_data_report'
    _inherit = "report.report_xlsx.abstract"

    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.payslip'].browse(docids)
        return {'docs': docs}

    def generate_xlsx_report(self, workbook, data, payslips):
        sheet = workbook.add_worksheet('Payslip Report')

        title_format = workbook.add_format({
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 18
        })

        header_format = workbook.add_format({
            'num_format': '#,##0.00',
            'bold': True,
            'bg_color': '#D9D9D9',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        rule_values_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
        })

        unique_rule_names = [
            "Standard Gross Salary", "Basic Salary", "Notice Pay", "Absent Deduction",
            "Late Deduction", "Food Allowance", "Conveyance Allowance / Fuel Allowance",
            "Salary Deduction", "Other Deduction", "Salary Arrear", "Other Allowance",
            "Mobile Allowance", "Gratuity", "House Rent", "Gratuity Adjustment",
            "Bonus", "Overtime", "Gross Salary", "Conveyance Allowance Deduction", "I.Tax",
            "Vehicle Return Amount", "Comp Loan", "Vehicle Loan", "Advance Salary",
            "PF Employee", "PF Loan", "EOBI Employee", "Pending EOBI",
            "Deduction Vehicle Repair & Maint.", "Income Tax", "Other Deduction",
            "Net Salary","Zakat","PF Net", "Net Payable", "PF Employer", "EOBI Employer"
        ]

        headers = [
            'Employee Name', 'Period', 'Contract', 'Batch','Last Working Date','Worked Days', 'Total Days in Month','Total Sundays','Structure','Badge ID','Company Name',
            'Department', 'Designation', 'Location', 'Grade','Employee Type', 'Analytics', 'Employee Bank', 'Employer Bank'] + unique_rule_names


        column_widths = [len(str(header)) for header in headers + unique_rule_names]
        rule_grand_totals = {rule: 0.0 for rule in unique_rule_names}

        sheet.merge_range(0, 0, 1, len(headers) - 1, 'Employee Payslip Data Report', title_format)


        for col, header in enumerate(headers):
            sheet.write(2, col, header, header_format)

        sorted_payslips = sorted(payslips, key=lambda rec: rec.employee_id.barcode or '')

        for row, rec in enumerate(sorted_payslips, start=3):
            period = rec.date_from.strftime('%m/%d/%Y') + ' - ' + rec.date_to.strftime('%m/%d/%Y')

            base_data = [
                rec.employee_id.name,
                period or '',
                rec.contract_id.name or '',
                rec.payslip_run_id.name or '',
                rec.last_work_date if rec.last_work_date else '',
                rec.count_days if rec.count_days else '',
                # 'N/A',
                # 'N/A',
                # 'N/A',
                # 'N/A',
                rec.cal_days or '',
                rec.sunday_count or '',
                rec.struct_id.name or '',
                rec.x_studio_related_field_6p0_1i0ba84fv if rec.x_studio_related_field_6p0_1i0ba84fv else 'N/A',
                rec.x_studio_company_name.name if rec.x_studio_company_name.name else 'N/A',
                # 'N/A',
                # 'N/A',
                rec.emp_department_id.name or '',
                rec.emp_job_id.name or '',
                rec.emp_location_id.name or '',
                rec.emp_employee_grade or '',
                rec.emp_employee_type or '',
                rec.emp_analytics.name or '',
                rec.emp_employee_bank or '',
                rec.emp_employer_bank.acc_number or '',
            ]

            rule_totals = {}
            for line in rec.line_ids:
                rule_totals[line.salary_rule_id.name] = rule_totals.get(line.salary_rule_id.name, 0.0) + line.total

            for rule_name in unique_rule_names:
                value = rule_totals.get(rule_name)
                if isinstance(value, (int, float)):
                    rule_grand_totals[rule_name] += value
                    base_data.append(value)
                else:
                    base_data.append('N/A')

            for col, val in enumerate(base_data):
                if isinstance(val, (int, float)):
                    sheet.write_number(row, col, val, rule_values_format)
                else:
                    sheet.write(row, col, str(val))

                if len(str(val)) > column_widths[col]:
                    column_widths[col] = len(str(val))



        for col, width in enumerate(column_widths):
            sheet.set_column(col, col, width + 3)

        total_row = len(payslips) + 3

        sheet.merge_range(total_row, 0, total_row, 18, 'TOTAL', header_format)

        for idx, rule_name in enumerate(unique_rule_names):
            total = rule_grand_totals.get(rule_name)
            if isinstance(total, (int, float)):
                sheet.write_number(total_row, 19 + idx, total, header_format)
            else:
                sheet.write(total_row, 19 + idx, 'N/A', header_format)

