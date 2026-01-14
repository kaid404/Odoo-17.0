from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta

from dateutil import relativedelta

import logging

_logger = logging.getLogger(__name__)


class CampusSummaryReport(models.TransientModel):
    _name = 'campus.summary'
    _description = 'Campus Summary Report'

    date_from = fields.Date(string='Date From', required=True, default=lambda self: datetime.today().replace(day=1).date())
    date_to = fields.Date(string='Date To', required=True, default=datetime.today())

    # def print_pdf_action(self):
    #     url = "https://web.whatsapp.com/send?l=&phone=" + '+923360006307' + "&text=" + 'Sent massage'
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': url,
    #         'target': 'self     ',
    #     }

    def print_pdf_action(self):
        _logger.info('----------------------print_pdf_action--------------------------------------------')
        companies = self.sudo().env.companies or self.sudo().env.user.company
        campus_data = []
        left_student_lines = []

        payment_count = 0
        payment_amount = 0
        payment_rec_perc = 0
        bal_count = 0
        bal_amount = 0
        bal_perc = 0
        t_payment = 0
        for rec in companies:
            rec =rec.sudo()
            
            students = self.env['op.student'].sudo().search_count([('company_id', '=', rec.id)])
            left = self.env['op.student'].sudo().search([('company_id', '=', rec.id), ('state', '=', 'left')])
            print('left--->>', left)

            Tuition_ids = self.env['account.move.line'].sudo().search([
                ('product_id.name', '=', 'Tuition Fee'),
                ('move_id.company_id', '=', rec.id),
                ('move_id.student_id', '!=', False),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice']),
                ('move_id.invoice_date', '>=', self.date_from),
                ('move_id.invoice_date', '<=', self.date_to),
                ('move_id.payment_state', 'in', ['paid','in_payment'])
                # Only unpaid or partially paid invoices
            ])
            _logger.info(Tuition_ids)
            _logger.info('Tuition_ids')

            tuition_total = sum(Tuition_ids.mapped('price_subtotal'))
            Fee_Arrears = self.env['account.move.line'].sudo().search([
                ('product_id.name', '=', 'Fee Arrears'),
                ('move_id.company_id', '=', rec.id),
                ('move_id.student_id', '!=', False),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice']),
                ('move_id.invoice_date', '>=', self.date_from),
                ('move_id.invoice_date', '<=', self.date_to),
               
                ('move_id.payment_state', '=', 'paid')
                # Only unpaid or partially paid invoices
            ])

            Fee_Arrears = sum(Fee_Arrears.mapped('price_subtotal'))

            advance_dates_ids = self.env['account.move'].sudo().search([
                ('company_id', '=', rec.id),
                ('student_id', '!=', False),
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('payment_state', '=', 'paid'), ('invoice_date', '>', self.date_from),
                ('invoice_date', '<=', self.date_to)
                # Only unpaid or partially paid invoices
            ])

            advance_dates = advance_dates_ids.mapped('invoice_date')
            _logger.info('---------------2222----------------')
            unique_dates = sorted(set(advance_dates))
            advance_rec = []
            advance_amt = 0
            for adv in unique_dates:
                advance_dates_ids = self.env['account.move'].sudo().search([
                    ('company_id', '=', rec.id),
                    ('state', '=', 'posted'),
                    ('student_id', '!=', False),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('payment_state', '=', 'paid'), ('invoice_date', '=', adv)
                    # Only unpaid or partially paid invoices
                ])
                advance_rec.append({'date': adv, 'amount': sum(advance_dates_ids.mapped('amount_total'))})
                advance_amt += sum(advance_dates_ids.mapped('amount_total'))

            # advance_dates_ids = self.env['account.move'].search([
            #     ('company_id', '=', rec.id),
            #     ('student_id', '!=', False),
            #     ('state', '=', 'posted'),
            #     ('move_type', 'in', ['out_invoice', 'out_refund']),
            #     ('payment_state', '=', 'paid'), ('invoice_date', '>', self.date_from)
            #     # Only unpaid or partially paid invoices
            # ])

            paid_dates = [self.date_from - relativedelta.relativedelta(months=1),
                          self.date_from - relativedelta.relativedelta(months=2)]

            # unique_dates = sorted(set(advance_dates))
            paid_rec = []
            paid_amt = 0
            for adv in paid_dates:
                paid_dates_ids = self.env['account.move'].sudo().search([
                    ('company_id', '=', rec.id),
                    ('state', '=', 'posted'),
                    ('student_id', '!=', False),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('payment_state', '=', 'paid'), ('invoice_date', '=', adv)
                    # Only unpaid or partially paid invoices
                ])

                if sum(paid_dates_ids.mapped('amount_total')) > 0:
                    paid_rec.append({'date': adv, 'amount': sum(paid_dates_ids.mapped('amount_total'))})
                paid_amt += sum(paid_dates_ids.mapped('amount_total'))
            _logger.info('---------------33333----------------')
            left_stds_amount = self.env['account.move'].sudo().search([
                ('student_id', 'in', left.ids),
                ('state', '=', 'posted'),
                ('student_id', '!=', False),
                ('move_type', 'in', ['out_invoice']),
                ('amount_residual', '>', 0), ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to)  # Only unpaid or partially paid invoices
            ])
            print('left_stds_amount--->>', left_stds_amount)
            for lft_std in left_stds_amount:
                left_student_lines.append({
                    'campus': lft_std.student_id.company_id.name,
                    'roll_nbr': lft_std.student_id.gr_no,
                    'std_name': lft_std.student_id.name,
                    'write_date': lft_std.student_id.write_date.date(),
                    'amount': lft_std.amount_total,
                })
            print('left_student_lines--->>', left_student_lines)
            prev_data = self.env['account.move'].sudo().search([
                ('company_id', '=', rec.id),
                ('state', '=', 'posted'),
                ('student_id', '!=', False),
                ('move_type', 'in', ['out_invoice']),
                ('amount_residual', '>', 0), ('invoice_date_due', '<', self.date_from)
                # Only unpaid or partially paid invoices
            ])

            Fee_Arrears_xyz = self.env['account.move.line'].sudo().search([
                ('product_id.name', '=', 'Fee Arrears'),
                ('move_id.company_id', '=', rec.id),
                ('move_id.student_id', '!=', False),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice']),
                ('move_id.invoice_date', '>=', self.date_from),
                ('move_id.invoice_date', '<=', self.date_to),
               
                ('move_id.state', '=', 'posted')
                # Only unpaid or partially paid invoices
            ])

            Fee_Arrears_xyz = sum(Fee_Arrears_xyz.mapped('price_subtotal'))
            
            current_month = self.env['account.move'].sudo().search([
                ('company_id', '=', rec.id),
                ('state', '=', 'posted'),
                ('student_id', '!=', False),
                ('is_fee_invoice', '!=', False),
                ('move_type', 'in', ['out_invoice']),
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to)  # Only unpaid or partially paid invoices
            ])
            _logger.info(f'>>>>>>>>>>>>>>>{current_month}')
            left_stds_amount_xyz = left_stds_amount
            arrears = Fee_Arrears_xyz
            left_stds_amount = sum(left_stds_amount.mapped('amount_residual'))
            current = sum(current_month.mapped('amount_total')) - Fee_Arrears_xyz
            total = arrears + current
            # left
            # left ends
            _logger.info('---------------4444444----------------')

            fine_amt = self.env['account.move'].sudo().search([
                ('super_invoice', '!=', False),
                ('company_id', '=', rec.id),
                ('payment_state', '=', 'paid'),
                ('state', '=', 'posted'),
                ('student_id', '!=', False),
                ('move_type', 'in', ['out_invoice']),
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to)  # Only unpaid or partially paid invoices
            ])


            
            fine_amt = self.env['account.move.line'].sudo().search([
                ('product_id.name', '=', 'Late Fee'),
                ('move_id.company_id', '=', rec.id),
                ('move_id.student_id', '!=', False),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice']),
                ('move_id.invoice_date', '>=', self.date_from),
                ('move_id.invoice_date', '<=', self.date_to),
                ('move_id.payment_state', 'in', ['paid','in_payment'])
                # Only unpaid or partially paid invoices
            ])
            _logger.info(Tuition_ids)
            _logger.info('Tuition_ids')

            fine_amt = sum(fine_amt.mapped('price_subtotal'))



            
            adm_amt = self.env['account.move.line'].sudo().search([
                ('product_id.name', '=', 'Admission Fee'),
                ('move_id.company_id', '=', rec.id),
                ('move_id.student_id', '!=', False),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice']),
                ('move_id.invoice_date', '>=', self.date_from),
                ('move_id.invoice_date', '<=', self.date_to),
                ('move_id.payment_state', 'in', ['paid','in_payment'])
                # Only unpaid or partially paid invoices
            ])
            _logger.info(Tuition_ids)
            _logger.info('Tuition_ids')

            adm_amt = sum(adm_amt.mapped('price_subtotal'))
            # arrears = sum(prev_data.mapped('amount_residual'))
            #fine_amt = sum(fine_amt.mapped('amount_residual'))

            payments = self.env['account.payment'].sudo().search([
                ('company_id', '=', rec.id),
                ('state', '=', 'posted'),
                ('payment_type', 'in', ['inbound']),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to)
            ])

            payments = self.env['account.move'].sudo().search([
                ('company_id', '=', rec.id),
                ('state', '=', 'posted'),
                ('student_id', '!=', False),
                ('is_fee_invoice', '!=', False),
                ('move_type', 'in', ['out_invoice']),
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                 ('payment_state','in',['paid','in_payment','partial'])# Only unpaid or partially paid invoices
            ])
            payment_count = len(payments)


            payment_amount = sum(payments.mapped('amount_total')) - sum(payments.mapped('amount_residual'))
            payment_rec_perc = 0
            if total != 0:
                payment_rec_perc = round((payment_amount / total) * 100, 2)
            
            bal_count = len(current_month) - payment_count
            bal_amount = total - payment_amount
            bal_perc = 0
            left_std_percentage = 0
            if total != 0:
                bal_perc = round(bal_amount / total * 100, 2)
                left_std_percentage = round(left_stds_amount / total * 100, 2)
            t_payment +=  payment_amount
            _logger.info('---------------555555----------------')
            campus_data.append({
                'nos': len(current_month),
                'name': rec.name,
                'arrears': arrears,
                'current': current,
                'total': total,
                'received_count': payment_count,
                'received': payment_amount,
                'received_perc': f'{payment_rec_perc}%',
                'bal_count': bal_count,
                'bal_amount': bal_amount,
                'bal_perc': f'{bal_perc}%',
                'left_count': len(left_stds_amount_xyz),
                'left_stds_amount': left_stds_amount,
                'left_std_percentage': f'{left_std_percentage}%',
                'total_after_left_amount': total - left_stds_amount,
            })

        fee_arrears = Fee_Arrears
        res = {
            # 'form_data': self.read()[0],
            'tuition_total': tuition_total,
            'fee_arrears': fee_arrears,
            'fine_amt': fine_amt,
            'f_fee': tuition_total + fee_arrears + fine_amt,
            'campus_data': campus_data,
            'advance_rec': advance_rec,
            'paid_rec': paid_rec,
            'advance_amt': advance_amt,
            'paid_amt': paid_amt,
            'from_date': self.date_from,
            'to_date': self.date_to
        }
        data = {
            'left_student_lines': left_student_lines,
            # 'company_logo': companies.logo,
            'form': res,
            'tuition_total': round(tuition_total,2),
            'fee_arrears': round(fee_arrears),
            'fine_amt': round(fine_amt,2),
            'adm_amt':adm_amt,
            'f_total_amt':round(t_payment,2),
            'f_fee': round(tuition_total + fee_arrears + fine_amt,2),
            'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        # print(data)
        _logger.info('---------------66666----------------')

        return self.env.ref('campus_summary_report.campus_summary').report_action(self, data=data)
