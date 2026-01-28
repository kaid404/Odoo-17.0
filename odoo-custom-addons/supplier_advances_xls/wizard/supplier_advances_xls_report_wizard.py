from odoo import models, fields, api, _
import io
import base64

try:
    from odoo.tools.misc import xlsxwriter
except Exception:
    import xlsxwriter
from datetime import datetime


class SupplierAdvancesXlsReportWizard(models.TransientModel):
    _name = 'supplier.advances.xls.report.wizard'
    _description = 'Supplier Advances XLS Report Wizard'

    journal_id = fields.Many2many(
        'account.journal',
        string='Journal',
        domain=[('type', 'in', ['bank', 'cash'])]
    )
    date_as = fields.Date(string='As On Date', required=True, default=fields.Date.context_today)

    def _get_payment_bank_date(self, payment):
        statement_line = self.env['account.bank.statement.line'].search([
            ('payment_ref', '=', payment.name),
            ('amount', '<', 0)
        ], limit=1)

        if statement_line and statement_line.date:
            return statement_line.date

        statement_line = self.env['account.bank.statement.line'].search([
            ('payment_ref', '=', payment.name)
        ], limit=1)

        if statement_line and statement_line.date:
            if statement_line.amount < 0 and abs(statement_line.amount - (-payment.amount)) < 0.01:
                return statement_line.date

        if payment.move_id:
            bank_lines = payment.move_id.line_ids.filtered(
                lambda line: line.account_id.internal_group == 'liquidity'
            )
            for line in bank_lines:
                if line.statement_line_id and line.statement_line_id.date:
                    if line.statement_line_id.amount < 0:  # Outbound
                        return line.statement_line_id.date

        return payment.date

    def _get_po_info_from_payment(self, payment):
        po_name = ''
        purchaser = ''
        untaxed_amount = 0.0
        total_amount = 0.0
        warehouse = ''

        if payment.purchase_id:
            po_name = payment.purchase_id.name or ''
            if payment.purchase_id.user_id:
                purchaser = payment.purchase_id.user_id.name or ''
            untaxed_amount = payment.purchase_id.amount_untaxed
            total_amount = payment.purchase_id.amount_total
            if payment.purchase_id.picking_type_id and payment.purchase_id.picking_type_id.warehouse_id:
                warehouse = payment.purchase_id.picking_type_id.warehouse_id.name or ''
            return po_name, purchaser, untaxed_amount, total_amount, warehouse

        if payment.purchase_idss:
            po_name = purchaser = warehouse = ''
            untaxed_amount = 0.0
            total_amount = 0.0

            for purchase_id in payment.purchase_idss:
                if not po_name:
                    po_name = purchase_id.name or ''
                else:
                    po_name = po_name + ', ' + purchase_id.name
                if purchase_id.user_id:
                    if not purchaser:
                        purchaser = purchase_id.user_id.name or ''
                    else:
                        purchaser = purchaser + ', ' + purchase_id.user_id.name

                untaxed_amount += purchase_id.amount_untaxed or 0.0
                total_amount += purchase_id.amount_total or 0.0

                if purchase_id.picking_type_id and purchase_id.picking_type_id.warehouse_id:
                    wh_name = purchase_id.picking_type_id.warehouse_id.name or ''
                    if wh_name and wh_name not in warehouse:
                        warehouse = wh_name if not warehouse else warehouse + ', ' + wh_name

            return po_name, purchaser, untaxed_amount, total_amount, warehouse
        return '', '', 0.0, 0.0, ''

        if payment.payment_reference:
            po_record = self.env['purchase.order'].search([
                ('name', '=', payment.payment_reference)
            ], limit=1)
            if po_record:
                po_name = po_record.name or ''
                if po_record.user_id:
                    purchaser = po_record.user_id.name or ''
                return po_name, purchaser

        if payment.move_id:
            for line in payment.move_id.line_ids:
                if line.ref:
                    po_record = self.env['purchase.order'].search([
                        ('name', '=', line.ref)
                    ], limit=1)
                    if po_record:
                        po_name = po_record.name or ''
                        if po_record.user_id:
                            purchaser = po_record.user_id.name or ''
                        return po_name, purchaser

        po_records = self.env['purchase.order'].search([
            ('partner_id', '=', payment.partner_id.id),
            ('date_order', '<=', payment.date),
            ('state', 'in', ['purchase', 'done'])
        ], order='date_order desc', limit=5)

        for po_record in po_records:
            if abs(po_record.amount_total - payment.amount) <= (po_record.amount_total * 0.2):  # 20% tolerance
                po_name = po_record.name or ''
                if po_record.user_id:
                    purchaser = po_record.user_id.name or ''
                return po_name, purchaser

        return po_name, purchaser

    def _get_exclusive_sales_tax_amount(self, payment):
        """Get exclusive sales tax amount from payment lines"""
        exclusive_tax_amount = 0.0

        # Check if payment has lines with exclusive sales tax amount
        if hasattr(payment, 'payment_line_ids') and payment.payment_line_ids:
            for line in payment.payment_line_ids:
                if hasattr(line, 'amount_exclusive_sales_tax'):
                    exclusive_tax_amount += line.amount_exclusive_sales_tax or 0.0

        return exclusive_tax_amount

    def action_generate_xls_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Supplier Advances')

        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#D9D9D9', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        text_format = workbook.add_format({'border': 1, 'valign': 'vcenter'})
        text_wrap_format = workbook.add_format({'border': 1, 'text_wrap': True, 'valign': 'vcenter'})
        amount_format = workbook.add_format(
            {'border': 1, 'num_format': '#,##0.00', 'align': 'right', 'valign': 'vcenter'})
        total_format = workbook.add_format(
            {'bold': True, 'bg_color': '#F2F2F2', 'num_format': '#,##0.00', 'align': 'right', 'border': 1,
             'valign': 'vcenter'})

        company = self.env.company
        company_name = company.name or 'Pak Gulf Construction Pvt Ltd'

        worksheet.merge_range(0, 0, 0, 13, company_name, title_format)
        worksheet.merge_range(1, 0, 1, 13, 'Unadjusted Suppliers Advances Status Report', title_format)
        worksheet.merge_range(2, 0, 2, 13, f"As at {self.date_as.strftime('%d-%b-%y')}", title_format)

        # Handle Many2many field correctly - show selected journals or "All Journals"
        # if self.journal_id:
        #     journal_names = self.journal_id.mapped('name')
        #     journal_display_name = ', '.join(journal_names)
        # else:
        #     journal_display_name = 'All Journals'

        # worksheet.merge_range(3, 0, 3, 10, f'Journal: {journal_display_name}', title_format)

        headers = [
            'Sr. No', 'Payment Date', 'Payment Reference', 'Journal', 'PO No',
            'Purchaser','Amount Excluding Tax', 'Amount Including Tax', 'Warehouse', 'Suppliers Name', 'Analytic Account', 'Exclusive sale tax amount',
            'Amount', 'Pending Days'
        ]
        worksheet.write_row(5, 0, headers, header_format)

        domain = [
            ('date', '<=', self.date_as),
            ('state', '=', 'posted'),
            ('payment_type', '=', 'outbound'),
            ('amount', '>', 0),
        ]

        # Only filter by journal if journals are selected
        if self.journal_id:
            domain.append(('journal_id', 'in', self.journal_id.ids))

        payments = self.env['account.payment'].search(domain, order='date asc')

        row = 6
        sr = 1
        total_amount = 0.0
        total_exclusive_tax = 0.0
        today = fields.Date.from_string(self.date_as)

        processed_payment_refs = set()

        for payment in payments:
            payment_ref = payment.payment_reference or payment.ref or payment.name or ''
            if payment_ref in processed_payment_refs:
                continue
            processed_payment_refs.add(payment_ref)

            if payment.amount <= 0:
                continue

            has_attached_bills = payment.reconciled_bill_ids or payment.purchase_id

            if has_attached_bills:
                should_include = False

                if payment.reconciled_bill_ids:
                    pending_bills = payment.reconciled_bill_ids.filtered(
                        lambda bill: bill.state == 'posted' and hasattr(bill,
                                                                        'amount_residual') and bill.amount_residual > 0
                    )
                    if pending_bills:
                        should_include = True

                elif payment.purchase_id:
                    if payment.purchase_id.invoice_ids:
                        pending_bills = payment.purchase_id.invoice_ids.filtered(
                            lambda inv: inv.state == 'posted' and hasattr(inv,
                                                                          'amount_residual') and inv.amount_residual > 0
                        )
                        if pending_bills:
                            should_include = True

                if not should_include:
                    continue
            else:
                should_include = True

            po_name, purchaser, untaxed_amount, total_amount, warehouse = self._get_po_info_from_payment(payment)

            # Get Journal name
            journal_name = payment.journal_id.name or ''

            # Get Analytic Account
            analytic_account = ''
            if hasattr(payment, 'x_studio_analytic_account_1') and payment.x_studio_analytic_account_1:
                analytic_account = payment.x_studio_analytic_account_1.name or ''

            # Get Exclusive Sales Tax Amount
            exclusive_tax_amount = self._get_exclusive_sales_tax_amount(payment)

            payment_amount = payment.amount
            supplier = payment.partner_id.name or ''

            payment_date = self._get_payment_bank_date(payment)
            pending_days = ''
            if payment_date:
                try:
                    pd = fields.Date.from_string(payment_date)
                    pending_days = (today - pd).days
                except Exception:
                    pending_days = ''

            worksheet.write(row, 0, sr, text_format)
            worksheet.write(row, 1, payment_date.strftime('%d-%b-%y') if payment_date else '', text_format)
            worksheet.write(row, 2, payment.name, text_wrap_format)
            worksheet.write(row, 3, journal_name, text_format)
            worksheet.write(row, 4, po_name, text_format)
            worksheet.write(row, 5, purchaser, text_format)
            worksheet.write(row, 6, untaxed_amount, text_format)
            worksheet.write(row, 7, total_amount, text_format)
            worksheet.write(row, 8, warehouse, text_format)
            worksheet.write(row, 9, supplier, text_wrap_format)
            worksheet.write(row, 10, analytic_account, text_format)
            worksheet.write(row, 11, float(exclusive_tax_amount), amount_format)
            worksheet.write(row, 12, float(payment_amount), amount_format)
            worksheet.write(row, 13, pending_days if pending_days != '' else '', text_format)

            total_amount += float(payment_amount)
            total_exclusive_tax += float(exclusive_tax_amount)
            row += 1
            sr += 1

        if row > 6:
            worksheet.merge_range(row, 0, row, 10, 'Total Amount:', header_format)
            worksheet.write(row, 11, total_exclusive_tax, total_format)
            worksheet.write(row, 12, total_amount, total_format)
        else:
            worksheet.merge_range(6, 0, 6, 13, 'No unadjusted advances found', title_format)

        # Set column widths - UPDATED VERSION
        worksheet.set_column('A:A', 8)  # Sr. No
        worksheet.set_column('B:B', 15)  # Payment Date
        worksheet.set_column('C:C', 25)  # Payment Reference
        worksheet.set_column('D:D', 40)  # Journal - INCREASED for full bank account display
        worksheet.set_column('E:E', 15)  # PO No
        worksheet.set_column('F:F', 20)  # Purchaser
        worksheet.set_column('G:G', 18)  # PO Untaxed Amount
        worksheet.set_column('H:H', 18)  # PO Total Amount
        worksheet.set_column('I:I', 22)  # Warehouse
        worksheet.set_column('J:J', 35)  # Suppliers Name - INCREASED for long supplier names
        worksheet.set_column('K:K', 25)  # Analytic Account - INCREASED for department names
        worksheet.set_column('L:L', 30)  # Exclusive sale tax amount - SLIGHTLY INCREASED
        worksheet.set_column('M:M', 15)  # Amount
        worksheet.set_column('N:N', 15)  # Pending Days

        for r in range(6, row + 1):
            worksheet.set_row(r, 25)

        workbook.close()
        output.seek(0)
        data = output.read()
        output.close()

        filename = f"Supplier_Advances_Unadjusted_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(data),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }