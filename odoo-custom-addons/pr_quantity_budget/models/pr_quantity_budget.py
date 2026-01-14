import logging
from odoo import api, fields, models, _
from collections import defaultdict
from odoo.exceptions import ValidationError

from datetime import date, timedelta

logger = logging.getLogger(__name__)


# models/quantity_budget.py


class QuantityBudget(models.Model):
    _name = 'quantity.budget'
    _inherit = ['mail.thread']
    _description = 'Quantity Budget'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', default='draft', tracking=True)
    name = fields.Char(string='Reference', required=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('quantity.budget'), tracking=True)
    description = fields.Text(string='Description', tracking=True)
    request_id = fields.Many2one('purchase.request', string='Purchase Request')
    line_ids = fields.One2many('quantity.budget.line', 'budget_id', string='Budget Lines', tracking=True)
    start_date = fields.Date('Start Data', store=True, tracking=True)
    end_date = fields.Date('End Data', store=True, tracking=True)
    department_id = fields.Many2one('stock.department', string='Department', trackimng=True)
    total_budget_amount = fields.Monetary(string="Total Budgeted Value",
                                          compute='_compute_budget_amounts',
                                          store=True,
                                          tracking=True)
    utilized_budget_amount = fields.Monetary(string="Utilized Budgeted Amount",
                                             compute='_compute_budget_amounts',
                                             store=True,
                                             tracking=True)
    available_budget_amount = fields.Monetary(string="Available Budgeted Amount",
                                              compute='_compute_budget_amounts',
                                              store=True,
                                              tracking=True)
    total_consumed_percentage = fields.Float(string="Total Consumed %", compute='_compute_budget_amounts', store=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=False,
                                  default=lambda self: self.env.company.currency_id)

    @api.depends('line_ids.total_quantity', 'line_ids.ordered_quantity', 'line_ids.remaining_quantity', 'line_ids.rate')
    def _compute_budget_amounts(self):
        for rec in self:
            total = 0.0
            utilized = 0.0
            remaining = 0.0
            for line in rec.line_ids:
                if rec.line_ids:
                    rate = line.rate
                    total += line.total_quantity * rate
                    utilized += line.ordered_quantity * rate
                    remaining += line.remaining_quantity * rate

                rec.total_budget_amount = total
                rec.utilized_budget_amount = utilized
                rec.available_budget_amount = remaining
                rec.total_consumed_percentage = round((utilized / total * 100) if total else 0)

    def action_draft(self):
        self.state = 'draft'

    def action_done(self):
        self.state = 'done'

    def action_exceed_qty(self):
        return {
            'name': _('Exceed Quantity'),
            'type': 'ir.actions.act_window',
            'res_model': 'quantity.budget.exceed.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_budget_id': self.id},
        }


class QuantityBudgetLine(models.Model):
    _name = 'quantity.budget.line'
    _inherit = ['mail.thread']
    _description = 'Quantity Budget Line'

    budget_id = fields.Many2one('quantity.budget', string='Budget')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=False, trackimng=True)
    location_id = fields.Many2one('stock.location', string='Location', required=True,
                                  domain="[('usage', '=', 'internal')]", trackimng=True)
    product_id = fields.Many2one('product.product', string='Product Variant', required=True, trackimng=True)
    uom_id = fields.Many2one(related='product_id.uom_id', string='Unit', trackimng=True)
    # department_id = fields.Many2one('stock.department', string='Department', trackimng=True)
    rate = fields.Monetary(string='Rate', trackimng=True)
    total_quantity = fields.Float(string='Total Budget Qty', required=True, trackimng=True)
    ordered_quantity = fields.Float(string='Utilized Budget Qty', compute='_compute_ordered_quantity', store=True,
                                    trackimng=True)
    remaining_quantity = fields.Float(string='Available Budget Qty', compute='_compute_remaining_quantity', store=True,
                                      trackimng=True)
    consumed_percentage = fields.Float(string='Total Consumed %', compute='_compute_consumed_percentage', store=True,
                                       tracking=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def open_related_lines(self):
        dep_id = self.budget_id.department_id.id
        prod_id = self.product_id
        last_date = date(2025, 7, 28)

        related_requests = self.env['purchase.request.line'].search(
            [('request_id.stock_depart', '=', dep_id), ('product_id', '=', prod_id.id),
             ('request_id.date_start', '>=', last_date)])

        action = {
            'name': 'Purchase Request Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', related_requests.ids)],
            'target': 'current',
        }
        return action

    @api.depends('ordered_quantity', 'total_quantity')
    def _compute_consumed_percentage(self):
        for rec in self:
            if rec.total_quantity > 0:
                rec.consumed_percentage = rec.ordered_quantity / rec.total_quantity

    @api.depends('total_quantity', 'ordered_quantity')
    def _compute_remaining_quantity(self):
        for line in self:
            line.remaining_quantity = line.total_quantity - line.ordered_quantity

    @api.model
    def create(self, vals):
        line = super(QuantityBudgetLine, self).create(vals)
        if line.budget_id:
            line.budget_id.message_post(
                body=_("New budget line created: %s - %s (%s)") % (
                    line.product_id.display_name,
                    line.total_quantity,
                    line.location_id.display_name
                )
            )
        return line

    def unlink(self):
        for line in self:
            if line.cod_invoice_id.state == 'done':
                raise ValidationError(_("You cannot delete a line when the invoice is in 'Done' state."))

    def write(self, vals):
        # Store old values before writing
        old_values = {
            line.id: {
                'remaining_quantity': line.remaining_quantity,
                'ordered_quantity': line.ordered_quantity,
                'total_quantity': line.total_quantity,
                'location_id': line.location_id.display_name,
                'product_id': line.product_id.display_name,
            }
            for line in self
        }

        result = super(QuantityBudgetLine, self).write(vals)

        # Post messages for changed lines
        for line in self:
            if line.budget_id:
                changes = []
                if 'remaining_quantity' in vals and old_values[line.id][
                    'remaining_quantity'] != line.remaining_quantity:
                    changes.append(_(
                        "Quantity changed from %s to %s") % (
                                       old_values[line.id]['remaining_quantity'],
                                       line.remaining_quantity
                                   ))
                if 'ordered_quantity' in vals and old_values[line.id]['ordered_quantity'] != line.ordered_quantity:
                    changes.append(_(
                        "Quantity changed from %s to %s") % (
                                       old_values[line.id]['ordered_quantity'],
                                       line.ordered_quantity
                                   ))
                if 'total_quantity' in vals and old_values[line.id]['total_quantity'] != line.total_quantity:
                    changes.append(_(
                        "Quantity changed from %s to %s") % (
                                       old_values[line.id]['total_quantity'],
                                       line.total_quantity
                                   ))
                if 'location_id' in vals and old_values[line.id]['location_id'] != line.location_id.display_name:
                    changes.append(_(
                        "Location changed from %s to %s") % (
                                       old_values[line.id]['location_id'],
                                       line.location_id.display_name
                                   ))
                if 'product_id' in vals and old_values[line.id]['product_id'] != line.product_id.display_name:
                    changes.append(_(
                        "Product changed from %s to %s") % (
                                       old_values[line.id]['product_id'],
                                       line.product_id.display_name
                                   ))

                if changes:
                    line.budget_id.message_post(
                        body=_(" %s:%s ") % (
                            line.product_id.display_name,
                            "<br/>".join(changes)
                        )
                    )
        return result

    def unlink(self):
        # Notify before deletion
        for line in self:
            if line.budget_id:
                line.budget_id.message_post(
                    body=_("Budget line deleted: %s - %s (%s)") % (
                        line.product_id.display_name,
                        line.total_quantity,
                        line.ordered_quantity,
                        line.remaining_quantity,
                        line.location_id.display_name
                    )
                )
        return super(QuantityBudgetLine, self).unlink()


class QuantityBudgetExceedWizard(models.TransientModel):
    _name = 'quantity.budget.exceed.wizard'
    _inherit = ['mail.thread']
    _description = 'Quantity Budget Exceed Wizard'

    budget_id = fields.Many2one('quantity.budget', string='Budget', required=True)

    exceed_qty = fields.Float(string='Quantity to Exceed', required=True)
    note = fields.Text(string='Reason')
    available_product_ids = fields.Many2many(
        'product.product',
        compute='_compute_available_products',
        store=False
    )

    product_id = fields.Many2many('product.product', string='Product Variant', required=True,
                                  domain="[('id', 'in', available_product_ids)]"
                                  # compute='_compute_available_products',
                                  )

    @api.depends('budget_id')
    def _compute_available_products(self):
        for wizard in self:
            wizard.available_product_ids = wizard.budget_id.line_ids.mapped('product_id')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self._context.get('default_budget_id'):
            res['budget_id'] = self._context['default_budget_id']
        return res

    def action_confirm(self):
        self.ensure_one()
        if self.exceed_qty <= 0:
            raise ValidationError(_('Quantity to exceed must be positive'))

        # Find or create the budget line for this product
        budget_line = self.env['quantity.budget.line'].search([
            ('budget_id', '=', self.budget_id.id),
            ('product_id', '=', self.product_id.id)
        ], limit=1)

        if not budget_line:
            # Create new line if product doesn't exist in budget
            budget_line = self.env['quantity.budget.line'].create({
                'budget_id': self.budget_id.id,
                'product_id': self.product_id.id,
                'warehouse_id': self.budget_id.line_ids[:1].warehouse_id.id if self.budget_id.line_ids else False,
                'location_id': self.budget_id.line_ids[:1].location_id.id if self.budget_id.line_ids else False,
                'total_quantity': self.exceed_qty,
            })
        else:
            # Update existing line
            budget_line.write({
                'total_quantity': budget_line.total_quantity + self.exceed_qty,
            })

        return {'type': 'ir.actions.act_window_close'}
