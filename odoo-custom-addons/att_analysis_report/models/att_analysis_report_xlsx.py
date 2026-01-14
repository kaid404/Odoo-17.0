from odoo import models
from datetime import datetime


class AttAnalysisReportXlsx(models.AbstractModel):
    _name = 'report.att_analysis_report.att_analysis_template_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('Attendance Analysis')

        title_fmt = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center'
        })

        header_fmt = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'bg_color': '#007bff',
            'font_color': 'white'
        })

        text_fmt = workbook.add_format({
            'border': 1,
            'align': 'left'
        })

        center_fmt = workbook.add_format({
            'border': 1,
            'align': 'center'
        })

        employee_lines = data.get('employee_lines', [])
        report_of = data.get('report_of')
        show_email = data.get('show_email')
        period = data.get('period')

        if show_email:
            sheet.merge_range('A1:H1', 'Reports for Lates, Leaves & Absences', title_fmt)
            sheet.merge_range('A2:H2', period, center_fmt)
        else:
            sheet.merge_range('A1:G1', 'Reports for Lates, Leaves & Absences', title_fmt)
            sheet.merge_range('A2:G2', period, center_fmt)
        row = 4
        col = 0

        headers = ['S#']

        if show_email:
            headers.append('Email')

        headers += [
            'Employee',
            'Team',
            'Badge ID',
            'Manager',
            'Designation'
        ]

        if report_of == 'leaves':
            headers.append('Total Leave')
        elif report_of == 'absences':
            headers.append('Total Absences')
        elif report_of == 'lates':
            headers.append('Total Lates')

        for header in headers:
            sheet.write(row, col, header, header_fmt)
            sheet.set_column(col, col, 18)
            col += 1

        row += 1
        sr = 1

        for line in employee_lines:
            col = 0
            sheet.write(row, col, sr, center_fmt)
            col += 1

            if show_email:
                sheet.write(row, col, line.get('email', ''), text_fmt)
                col += 1

            sheet.write(row, col, line.get('employee_name') or '-', text_fmt)
            col += 1
            sheet.write(row, col, line.get('team', '') or '-', text_fmt)
            col += 1
            sheet.write(row, col, line.get('code', '') or '-', center_fmt)
            col += 1
            sheet.write(row, col, line.get('manager', '') or '-', text_fmt)
            col += 1
            sheet.write(row, col, line.get('designation', '') or '-', text_fmt)
            col += 1

            if report_of == 'leaves':
                sheet.write(row, col, line.get('leave_days', 0), center_fmt)
            elif report_of == 'absences':
                sheet.write(row, col, line.get('absent_days', 0), center_fmt)
            elif report_of == 'lates':
                sheet.write(row, col, line.get('late_days', 0), center_fmt)

            row += 1
            sr += 1

            sheet.set_column('A:A', 7)
            sheet.set_column('B:B', 30)