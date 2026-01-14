from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)


class CityBooksLedger(models.TransientModel):
    _name = 'city.books.ledger.report'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    product_ids = fields.Many2many('product.template', string="Book or Note Book Name", domain="[('type', '!=', 'service')]")
    category_id = fields.Many2one('product.category', string="Category Name", domain="[('name', 'ilike', 'Book')]")


    def product_ledger_report(self):
        record_list = []
        category_dict = {}
        if self.product_ids:
            products = self.env['product.template'].search([('id', 'in', self.product_ids.ids)])
        elif self.category_id:
            products = self.env['product.template'].search([('categ_id', '=', self.category_id.id)])
        else:
            products = self.env['product.template'].search([('type', '!=', 'service')])

        for product in products:
            category = product.categ_id.name or 'Uncategorized'
            opening_moves = self.env['stock.move.line'].search([
                ('product_id.product_tmpl_id', '=', product.id),
                ('date', '<', self.from_date),
                ('reference', 'in', ['IN', 'Product Quantity Updated'])
            ])
            opening_qty = sum(opening_moves.mapped('quantity'))
            move_lines = self.env['stock.move.line'].search([
                ('product_id.product_tmpl_id', '=', product.id),
                ('date', '>=', self.from_date),
                ('date', '<=', self.to_date),
                ('state', '=', 'done')
            ])

            total_received = 0
            total_sold = 0
            balance_qty = opening_qty
            
            for line in move_lines:
                if line.location_id.usage in ['supplier', 'inventory'] and line.location_dest_id.usage == 'internal':
                    total_received += line.quantity
                elif line.location_id.usage == 'internal' and line.location_dest_id.usage in ['customer', 'production',
                                                                                              'inventory']:
                    total_sold += line.quantity
            
            balance_qty += total_received - total_sold
            product_data = {
                'product': product.name,
                'cost': product.standard_price,
                'sale_price': product.list_price,
                'opening_qty': opening_qty,
                'total_received': total_received,
                'total_sold': total_sold,
                'balance_qty': balance_qty,
            }
            if category in category_dict:
                category_dict[category].append(product_data)
            else:
                category_dict[category] = [product_data]
    
        res = {
                'category_dict': category_dict,
                'record_list': record_list,
                'company_name': self.env.user.company_id.name,
                'company_logo': self.env.user.company_id.logo,
                'from_date': self.from_date,
                'to_date': self.to_date,
            }

        data = {
            'rec': res,
        }

        return self.env.ref('cityschool_books_sale_ledger_report.city_books_ledger_report_action').report_action(self, data=data)
