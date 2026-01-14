from odoo import models, fields, api
from datetime import datetime, timedelta

def get_create_date(write_date):
        
    if write_date:
        create_date = write_date
        adjusted_time = create_date + timedelta(hours=5)
        formatted_time = adjusted_time.strftime('%Y-%m-%d %I:%M:%S %p')
        #print('formatted_time--->', formatted_time)
        #_logger.info(f'>>>>>>>>>{formatted_time}')
        return formatted_time
    else:
        return False



class FeeReportWizard(models.TransientModel):
    _name = 'fee.report.wizard'
    _description = 'Fee Report Wizard'

    date = fields.Date(string='Date', default=fields.Date.today)

    def print_report_data(self):
        today_start = datetime.combine(self.date, datetime.min.time())
        today_end = today_start + timedelta(days=1)

        final_list = []
        tuition_fee, fine, reg_pros, adm, sec, wav = 0, 0, 0, 0, 0, 0

        # Search students and prospectus within the date range
        #('write_date', '>=', today_start),
        #('write_date', '<', today_end),    

        payment_ids = self.env['account.payment'].search([('date','=',self.date),('company_id','in',self.env.context.get('allowed_company_ids', []))], order='write_date ASC',)
        inv_lst = []
        for p in  payment_ids:
            if len(p.reconciled_invoice_ids.ids) == 1:
                if p.reconciled_invoice_ids.is_fee_invoice == True:
                    inv_lst.append(p.reconciled_invoice_ids.id)        
            
        students = self.env['account.move'].search([
            ('id','in',inv_lst),('company_id','in',self.env.context.get('allowed_company_ids', [])),
            ('is_fee_invoice', '=', True),
            ('payment_state', 'in', ['paid', 'in_payment', 'partial'])
        ], order='write_date ASC',)
        prospectus = self.env['op.prospectus'].search([
            ('create_date', '>=', today_start),('company_id','in',self.env.context.get('allowed_company_ids', [])),
            ('create_date', '<', today_end)
        ], order='write_date ASC',)

        # Process Prospectus Data
        prosp_detail = [
            {
                'receipt_number': prospe.application_id.application_number,
                'name': prospe.applicant_name,
                'campus': prospe.company_id.name or 'N/A',
                'write_uid': prospe.create_uid.name or 'N/A',
                'write_date': get_create_date(prospe.write_date),
                'rec_date': prospe.create_date.date(),
                'std': prospe.application_id.student_id.id or 0,
                'reg_pros': prospe.amount or 0,
            }
            for prospe in prospectus
        ]

        # Process Fee Details
        fee_detail = []
        for student in students:
            line_totals = {
                line.product_id.name: line.price_total
                for line in student.invoice_line_ids
            }
            fee_detail.append({
                'receipt_number': student.name or 'N/A',
                'name': student.student_id.name or 'N/A',
                'std': student.student_id.id or 0,
                'campus': student.student_id.company_id.name or 'N/A',
                'section': student.student_id.section_id.name or 'N/A',
                'write_uid': student.write_uid.name or 'N/A',
                'write_date': student.get_create_date(),
                'roll_id': student.student_id.gr_no or 'N/A',
                'due_date': student.invoice_date_due,
                'rec_date': student.write_date.date(),
                'tuition': line_totals.get('Tuition Fee', 0),
                'fine': line_totals.get('Late Fee', 0),
                'sec': line_totals.get('Security Charges', 0),
                'adm': line_totals.get('Admission Fee', 0),
                'arrears': line_totals.get('Fee Arrears', 0),
                'recvd': student.amount_total - student.amount_residual or 0,
                'bln': sum(self.env['account.move'].search([('student_id','=',student.student_id.id),('payment_state','in',['not_paid']),('state','=','posted')]).mapped('amount_residual')),
                'reg_pros':line_totals.get('Registration Fee', 0),
                'wav': sum(
                    line.price_total
                    for line in student.invoice_line_ids
                    if line.product_id.name == 'Fee Waiver' or line.price_total < 0
                ) or 0,
            })

        # Combine Prospectus and Fee Details
        for prospe in prosp_detail:
            matched_fee = next((fee for fee in fee_detail if fee['std'] == prospe['std']), None)
            if matched_fee:
                final_list.append({
                    **matched_fee,
                    'reg_pros': prospe['reg_pros'],
                    'rec_date': prospe['rec_date'],
                })
                fee_detail.remove(matched_fee)
            else:
                final_list.append({
                    **prospe,
                    'tuition': 0,
                    'fine': 0,
                    'arrears': 0,
                    'recvd': 0,
                    'bln': 0,
                    'wav': 0,
                    'adm': 0,
                    'sec': 0,
                })

        final_list.extend(fee_detail)
        if final_list and 1==7:
            final_list = sorted(
            final_list,
            key=lambda x: datetime.strptime(x["write_date"], "%Y-%m-%d %I:%M:%S %p"))    

        # Prepare data for report
        data = {
            'rec': [{
                'date': self.date,
                'fee_details': fee_detail,
                'prosp_details': prosp_detail,
                'students': students,
                'prospectus': prospectus,
                'final_list': final_list,
                'campus':students[0].company_id.name if students else ''
            }]
        }

        return data

    def print_report(self):
        data = {'id':self.id}

        return self.env.ref('fee_report.action_fee_report_pdf').report_action(self, data=data)

    def cancel_action(self):
        return {'type': 'ir.actions.act_window_close'}
