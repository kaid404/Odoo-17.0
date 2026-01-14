from odoo import models, fields, api
from datetime import datetime, time, timedelta


class StockReport(models.Model):
    _name = 'stock.report'

    wizard_date = fields.Date(string='Date', required=True)
    wizard_location = fields.Many2many('stock.location', string='Location', required=True)

    def print_stock_report(self):
        date_start = datetime.combine(self.wizard_date, time.min)
        date_end = datetime.combine(self.wizard_date, time.max)

        date_opening = date_start - timedelta(minutes=1)

        print(date_start)
        print(date_end)

        product_sales = {}
        orders = self.env['pos.order'].search([
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_end),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ])


        for order in orders:
            for line in order.lines:
                product_id = line.product_id.id
                product_sales.setdefault(product_id, 0)
                product_sales[product_id] += line.qty

        results = []

        for product_id, qty_sold in product_sales.items():
            product = self.env['product.product'].browse(product_id)

            opening_stock_total = 0
            received_qty_total = 0
            issued_qty_total = 0


            for loc in self.wizard_location:


                # quants = self.env['stock.quant'].search([
                #     ('product_id', '=', product_id),
                #     ('location_id', '=', loc.id)
                #
                # ], order="in_date desc", limit=1)
                #
                # current_stock = quants.quantity if quants else 0

                total_moves_in = self.env['stock.move'].search([
                    ('product_id', '=', product_id),
                    ('location_dest_id', '=', loc.id),
                    ('company_id', '=', self.env.company.id),
                    ('state', '=', 'done'),
                    ('date', '<', date_start)

                ])
                total_received = sum(total_moves_in.mapped('product_uom_qty'))
                print(total_received)

                total_moves_out = self.env['stock.move'].search([
                    ('product_id', '=', product_id),
                    ('location_id', '=', loc.id),
                    ('company_id', '=', self.env.company.id),
                    ('state', '=', 'done'),
                    ('date', '<', date_start)
                ])
                total_issued = sum(total_moves_out.mapped('product_uom_qty'))

                opening_stock = total_received - total_issued

                moves_in = self.env['stock.move'].search([
                    ('product_id', '=', product_id),
                    ('location_dest_id', '=', loc.id),
                    ('company_id', '=', self.env.company.id),
                    ('state', '=', 'done'),
                    ('date', '>', date_start),
                    ('date', '<', date_end),

                ])
                received_qty = sum(moves_in.mapped('product_uom_qty'))
                print(received_qty)

                moves_out = self.env['stock.move'].search([
                    ('product_id', '=', product_id),
                    ('location_id', '=', loc.id),
                    ('company_id', '=', self.env.company.id),
                    ('state', '=', 'done'),
                    ('date', '>', date_start),
                    ('date', '<', date_end),

                ])
                issued_qty = sum(moves_out.mapped('product_uom_qty'))



                # opening_stock = current_stock - received_qty + issued_qty

                opening_stock_total += opening_stock
                received_qty_total += received_qty
                issued_qty_total += issued_qty

            closing_stock = opening_stock_total + received_qty_total - issued_qty_total

            results.append({
                'name': product.name,
                'opening_stock': opening_stock_total,
                'received_stock': received_qty_total,
                'issued_stock': issued_qty_total,
                'closing_stock': closing_stock,
            })

        report_data = {
            'report_date': self.wizard_date,
            'report_locations': ' - '.join(self.wizard_location.mapped('display_name')),
            'products': results
        }

        return self.env.ref('stock_report.action_report_stock_summary').report_action(self, data=report_data)

        # date_start = datetime.combine(self.wizard_date, time.min)
        # date_end = datetime.combine(self.wizard_date, time.max)
        #
        # print(date_start)
        # print(date_end)

        # orders = self.env['pos.order'].search([
        #     ('date_order', '>=', date_start),
        #     ('date_order', '<=', date_end),
        #     ('state', 'in', ['paid', 'done', 'invoiced']),
        # ])
        # print(orders)
        #
        # product_sales = {}
        # for order in orders:
        #     for line in order.lines:
        #         product_id = line.product_id.id
        #         product_sales.setdefault(product_id, 0)
        #         product_sales[product_id] += line.qty
        #
        #
        # results = []
        # for product_id, qty_sold in product_sales.items():
        #     product = self.env['product.product'].browse(product_id)
        #     inventory_location = self.env['stock.location'].search([
        #         ('usage', '=', 'inventory')
        #     ], limit=1)
        #     print(inventory_location)
        #
        #     quants = self.env['stock.quant'].search([('product_id', '=', product_id),('location_id.usage', '=', 'internal')])
        #
        #     for quant in quants:
        #         moves = self.env['stock.move'].search([
        #             ('product_id', '=', product_id),
        #             ('location_id', '=', quant.location_id.id),
        #             ('state', '=', 'done'),
        #             ('date', '>=', date_start),
        #             ('date', '<=', date_end),
        #         ])
        #
        #         total_units_transferred = sum(moves.mapped('product_uom_qty'))
        #
        #         moves_adj_out = self.env['stock.move'].search([
        #             ('product_id', '=', product_id),
        #             ('location_id', '=', quant.location_id.id),
        #             ('location_dest_id', '=', inventory_location.id),
        #             ('state', '=', 'done'),
        #             ('date', '>=', date_start),
        #             ('date', '<=', date_end),
        #         ])
        #         total_adj_out = sum(moves_adj_out.mapped('product_uom_qty'))
        #
        #         moves_adj_in = self.env['stock.move'].search([
        #             ('product_id', '=', product_id),
        #             ('location_id', '=', inventory_location.id),
        #             ('location_dest_id', '=', quant.location_id.id),
        #             ('state', '=', 'done'),
        #             ('date', '>=', date_start),
        #             ('date', '<=', date_end),
        #         ])
        #         total_adj_in = sum(moves_adj_in.mapped('product_uom_qty'))
        #
        #         total_units_adjusted = total_adj_in - total_adj_out
        #
        #
        #         results.append({
        #             'sku': product.default_code,
        #             'name': product.name,
        #             'location': quant.location_id.display_name,
        #             'unit_price': product.lst_price,
        #             'current_stock': quant.quantity,
        #             'sold_qty': qty_sold,
        #             'total_units_transferred': total_units_transferred,
        #             'total_units_adjusted': total_units_adjusted,
        #             'profit_percent': 0,
        #         })
        #
        #
