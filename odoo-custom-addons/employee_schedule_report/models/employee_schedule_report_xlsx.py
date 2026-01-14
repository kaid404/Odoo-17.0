from odoo import models


class SalarySheetXlsx(models.AbstractModel):
    _name = 'report.employee_schedule_report.employee_schedule_template_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):

        employees = data.get('employees', [])
        period = data.get('period', '')

        title_fmt = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center'
        })

        period_fmt = workbook.add_format({
            'bold': True, 'align': 'center'
        })

        header_fmt = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'bg_color': '#007bff',
            'font_color': 'white'
        })

        cell_fmt = workbook.add_format({
            'border': 1,
            'align': 'center'
        })

        info_fmt = workbook.add_format({
            'bold': True,
            'border': 1,
            'bg_color': '#f0f0f0'
        })

        total_fmt = workbook.add_format({
            'bold': True,
            'border': 1,
            'bg_color': '#e0e0e0',
            'num_format': '0.00'
        })

        for emp in employees:
            emp_info = emp['employee_info']
            lines = emp['lines']
            totals = emp['totals']

            sheet_name = emp_info['employee'][:31]
            sheet = workbook.add_worksheet(sheet_name)

            row = 0

            sheet.merge_range(row, 0, row, 8, 'Daily Attendance Report', title_fmt)
            row += 1
            sheet.merge_range(row, 0, row, 8, period, period_fmt)
            row += 2

            headers = [
                'Sr #', 'Date', 'Schedule', 'Scheduled In', 'Scheduled Out',
                'Actual In', 'Actual Out', 'Worked Time', 'Remarks'
            ]

            for col, h in enumerate(headers):
                sheet.write(row, col, h, header_fmt)

            row += 1


            sheet.merge_range(row, 0, row, 2, f"Employee: {emp_info['employee']}", info_fmt)
            sheet.merge_range(row, 3, row, 5, f"Department: {emp_info['dept']}", info_fmt)
            sheet.merge_range(row, 6, row, 8, f"Punch Code: {emp_info['code']}", info_fmt)
            row += 1

            sheet.merge_range(row, 0, row, 2, f"Team: {emp_info['team']}", info_fmt)
            sheet.merge_range(row, 3, row, 5, f"Job: {emp_info['Job']}", info_fmt)
            sheet.merge_range(row, 6, row, 8, f"Manager: {emp_info['manager']}", info_fmt)
            row += 1

            sr = 1
            for line in lines:
                sheet.write(row, 0, sr, cell_fmt)
                sheet.write(row, 1, line['date'], cell_fmt)
                sheet.write(row, 2, line['name'], cell_fmt)
                sheet.write(row, 3, line['scheduled_in'], cell_fmt)
                sheet.write(row, 4, line['scheduled_out'], cell_fmt)
                sheet.write(row, 5, line['check_in'], cell_fmt)
                sheet.write(row, 6, line['check_out'], cell_fmt)
                sheet.write(row, 7, line['worked_time'], cell_fmt)
                sheet.write(row, 8, line['remarks'], cell_fmt)

                sr += 1
                row += 1

            sheet.merge_range(
                row, 0, row, 1,
                f"Scheduled Time: {totals['scheduled_hours']}",
                total_fmt
            )
            sheet.merge_range(
                row, 2, row, 3,
                f"Worked Time: {round(totals['worked_hours'])}",
                total_fmt
            )
            sheet.merge_range(
                row, 4, row, 6,
                f"Total Scheduled Days: {totals['scheduled_days']}",
                total_fmt
            )
            sheet.merge_range(
                row, 7, row, 8,
                f"Total Late: {totals['late_days']}",
                total_fmt
            )
            row += 1

            sheet.merge_range(
                row, 0, row, 1,
                f"Total Half Day: {totals['half_days']}",
                total_fmt
            )
            sheet.merge_range(
                row, 2, row, 3,
                f"Total Absent Days: {totals['absent_days']}",
                total_fmt
            )
            sheet.merge_range(
                row, 4, row, 8,
                f"Full Day Leave: {totals['full_day_leaves']}",
                total_fmt
            )

            sheet.set_column('A:A', 7)
            sheet.set_column('B:B', 13)
            sheet.set_column('C:C', 22)
            sheet.set_column('D:G', 14)
            sheet.set_column('H:H', 14)
            sheet.set_column('I:I', 22)
