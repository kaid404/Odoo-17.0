# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields
from itertools import groupby
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sh_mrp = fields.Float(string="MRP")
    sh_tp = fields.Float(string="TP")
    sh_st_rate = fields.Char(string="ST Rate")
    sh_tax_amount = fields.Float(
        string="Sales Tax Amount", compute="compute_amounts")
    sh_st_amount = fields.Float(
        string="Amount Incl ST", compute="compute_amounts")
    sh_lot_id = fields.Many2one('stock.lot')

    def compute_amounts(self):
        for line in self:
            # assign tax amount for only sales tax
            sales_taxes = line.tax_ids.filtered(lambda m: m.sales_tax)
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = sales_taxes.compute_all(
                price,
                line.currency_id,
                line.quantity,
                line.product_id,
                line.partner_id
            )

            line.sh_tax_amount = sum(t.get('amount', 0.0)
                                     for t in taxes.get('taxes', []))
            # assign Amount Incl ST

            line.sh_st_amount = line.price_subtotal + line.sh_tax_amount


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_invoiced_lot_values(self):
        self.ensure_one()

        lot_values = super(AccountMove, self)._get_invoiced_lot_values()
        lv_2 = []
        for lot in lot_values:
            lot_id = lot['lot_id']
            if lot_id:
                lots = self.env['stock.lot'].browse(lot_id)
                if lots:
                    lot.update({
                        'expiration_date': lots.expiration_date,
                    })
            lv_2.append(lot)

        return lv_2


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        # Incremental sequencing to keep the lines order on the invoice.
        invoice_item_sequence = 0
        for order in self:
            order = order.with_company(order.company_id)
            # current_section_vals = None
            # down_payments = order.env['sale.order.line']

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:

                # sh-code _prepare_invoice_line calls multiple time lot wise
                stock_move_lines = line.move_ids.move_line_ids

                if not down_payment_section_added and line.is_downpayment:
                    # Create a dedicated section for the down payments
                    # (put at the end of the invoiceable_lines)
                    invoice_line_vals.append(
                        Command.create(
                            order._prepare_down_payment_section_line(sequence=invoice_item_sequence)
                        ),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1

                for move_line in stock_move_lines:
                    line_dict = line._prepare_invoice_line(
                        sequence=invoice_item_sequence, )

                    line_dict.update({
                        'quantity': move_line.quantity,
                        'sh_lot_id': move_line.lot_id.id
                    })

                    invoice_line_vals.append(
                        (0, 0, line_dict),
                    )
                    invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list and self._context.get('raise_if_nothing_to_invoice', True):
            raise UserError(self._nothing_to_invoice_error_message())

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(
                invoice_vals_list,
                key=lambda x: [
                    x.get(grouping_key) for grouping_key in invoice_grouping_keys
                ]
            )
            for grouping_keys, invoices in groupby(invoice_vals_list,
                                                   key=lambda x: [x.get(grouping_key) for grouping_key in
                                                                  invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ' , '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(
                        new=sequence, old=line[2]['sequence'])
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(
            default_move_type='out_invoice').create(invoice_vals_list)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total <
                                            0).action_switch_move_type()
        for move in moves:
            if final:
                # Downpayment might have been determined by a fixed amount set by the user.
                # This amount is tax included. This can lead to rounding issues.
                # E.g. a user wants a 100€ DP on a product with 21% tax.
                # 100 / 1.21 = 82.64, 82.64 * 1,21 = 99.99
                # This is already corrected by adding/removing the missing cents on the DP invoice,
                # but must also be accounted for on the final invoice.

                delta_amount = 0
                for order_line in self.order_line:
                    if not order_line.is_downpayment:
                        continue
                    inv_amt = order_amt = 0
                    for invoice_line in order_line.invoice_lines:
                        sign = 1 if invoice_line.move_id.is_inbound() else -1
                        if invoice_line.move_id == move:
                            inv_amt += invoice_line.price_total * sign
                        elif invoice_line.move_id.state != 'cancel':  # filter out canceled dp lines
                            order_amt += invoice_line.price_total * sign
                    if inv_amt and order_amt:
                        # if not inv_amt, this order line is not related to current move
                        # if no order_amt, dp order line was not invoiced
                        delta_amount += inv_amt + order_amt

                if not move.currency_id.is_zero(delta_amount):
                    receivable_line = move.line_ids.filtered(
                        lambda aml: aml.account_id.account_type == 'asset_receivable')[:1]
                    product_lines = move.line_ids.filtered(
                        lambda aml: aml.display_type == 'product' and aml.is_downpayment)
                    tax_lines = move.line_ids.filtered(
                        lambda aml: aml.tax_line_id.amount_type not in (False, 'fixed'))
                    if tax_lines and product_lines and receivable_line:
                        line_commands = [Command.update(receivable_line.id, {
                            'amount_currency': receivable_line.amount_currency + delta_amount,
                        })]
                        delta_sign = 1 if delta_amount > 0 else -1
                        for lines, attr, sign in (
                                (product_lines, 'price_total', -1 if move.is_inbound() else 1),
                                (tax_lines, 'amount_currency', 1),
                        ):
                            remaining = delta_amount
                            lines_len = len(lines)
                            for line in lines:
                                if move.currency_id.compare_amounts(remaining, 0) != delta_sign:
                                    break
                                amt = delta_sign * max(
                                    move.currency_id.rounding,
                                    abs(move.currency_id.round(remaining / lines_len)),
                                )
                                remaining -= amt
                                line_commands.append(Command.update(line.id, {attr: line[attr] + amt * sign}))
                        move.line_ids = line_commands

            move.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': move, 'origin': move.line_ids.sale_line_ids.order_id},
                subtype_xmlid='mail.mt_note',
            )
        return moves


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sh_mrp = fields.Float(string="MRP", compute="compute_amounts")
    sh_tp = fields.Float(string="TP", compute="compute_amounts")
    sh_st_rate = fields.Char(string="ST Rate", compute="compute_amounts")
    sh_tax_amount = fields.Float(
        string="Sales Tax Amount", compute="compute_amounts")
    sh_st_amount = fields.Float(
        string="Amount Incl ST", compute="compute_amounts")

    def compute_amounts(self):
        for line in self:
            line.sh_mrp = 0
            line.sh_tp = 0
            line.sh_st_rate = ''
            line.sh_tax_amount = 0
            line.sh_st_amount = 0

            # assign price to sh_mrp field
            pricelist = self.env['product.pricelist'].search(
                [('mrp', '=', True)], limit=1)
            if pricelist:
                price_data = pricelist._compute_price_rule(
                    line.product_template_id, line.product_uom_qty, date=fields.Date.today(), uom=line.product_uom)
                if price_data:
                    price = price_data[line.product_template_id.id][0]
                    line.sh_mrp = price

            # assign price to sh_tp field
            pricelist = self.env['product.pricelist'].search(
                [('tp', '=', True)], limit=1)
            if pricelist:
                price_data = pricelist._compute_price_rule(
                    line.product_template_id, line.product_uom_qty, date=fields.Date.today(), uom=line.product_uom)
                if price_data:
                    price = price_data[line.product_template_id.id][0]
                    line.sh_tp = price

            # assign price to price_unit field based on partner condition
            if line.order_partner_id.retailer_or_wholesaler == 'retailer':
                pricelist = self.env['product.pricelist'].search(
                    [('retailer_price', '=', True)], limit=1)
                if pricelist:
                    price_data = pricelist._compute_price_rule(
                        line.product_template_id, line.product_uom_qty, date=fields.Date.today(), uom=line.product_uom)
                    if price_data:
                        price = price_data[line.product_template_id.id][0]
                        line.price_unit = price

            elif line.order_partner_id.retailer_or_wholesaler == 'wholesaler':
                pricelist = self.env['product.pricelist'].search(
                    [('wholesale_price', '=', True)], limit=1)
                if pricelist:
                    price_data = pricelist._compute_price_rule(
                        line.product_template_id, line.product_uom_qty, date=fields.Date.today(), uom=line.product_uom)
                    if price_data:
                        price = price_data[line.product_template_id.id][0]
                        line.price_unit = price

            # assign tax name to st rate
            tax_names = ''
            sales_taxes = line.tax_id.filtered('sales_tax')
            count = 0
            tax_count = 0
            for tax in sales_taxes:
                if tax.children_tax_ids:
                    for child_tax in tax.children_tax_ids:
                        if count == 0:
                            tax_names = str(str(child_tax.amount).split('.')[0]) + '% '
                            count = 1
                            tax_count = 1
                        elif tax_count == 0 and count == 1:
                            tax_names = tax_names + ', ' + \
                                        str(str(child_tax.amount).split('.')[0]) + '% '
                            tax_count = 1
                        elif tax_count == 1 and count == 1:
                            tax_names = tax_names + '+ ' + \
                                        str(str(child_tax.amount).split('.')[0]) + '% '

                else:
                    if count == 0:
                        tax_names = str(str(tax.amount).split('.')[0]) + '% '
                        count = 1
                    else:
                        tax_names = tax_names + ', ' + str(str(tax.amount).split('.')[0]) + '% '

            line.sh_st_rate = tax_names

            # assign tax amount for only sales tax
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = sales_taxes.compute_all(
                price,
                line.currency_id,
                line.product_uom_qty,
                line.product_id,
                line.order_partner_id
            )

            line.sh_tax_amount = sum(t.get('amount', 0.0)
                                     for t in taxes.get('taxes', []))

            # assign Amount Incl ST

            line.sh_st_amount = line.price_subtotal + line.sh_tax_amount

    def _prepare_invoice_line(self, **optional_values):
        """Link timesheets to the created invoices. Date interval is injected in the
        context in sale_make_invoice_advance_inv wizard.
        """
        res = super()._prepare_invoice_line(**optional_values)

        # self.move_ids.mapped('lot_ids').ids

        res['sh_mrp'] = self.sh_mrp
        res['sh_tp'] = self.sh_tp
        res['sh_st_rate'] = self.sh_st_rate
        res['sh_tax_amount'] = self.sh_tax_amount
        res['sh_st_amount'] = self.sh_st_amount
        # res['sh_lot_ids'] = [(6,0,self.move_ids.mapped('lot_ids').ids)]

        return res
