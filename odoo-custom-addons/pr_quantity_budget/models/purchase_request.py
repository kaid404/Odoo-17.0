import logging
from odoo import api, fields, models, _
from collections import defaultdict
from odoo.exceptions import ValidationError

from datetime import date, timedelta

logger = logging.getLogger(__name__)


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    def button_to_approve(self):
        self.create_state_history(self.state)
        self.write({'state': 'to_approve'})
        self.activity_update()
        today_date = date.today()
        for req in self:
            if req.picking_type_id.id in [11,6]:
                for line in req.line_ids:
                    # dest_location = line.request_id.picking_type_id.default_location_dest_id
                    budget_lines = self.env['quantity.budget.line'].search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id', '=', line.request_id.picking_type_id.default_location_dest_id.id),
                        ('budget_id.department_id', '=', line.request_id.stock_depart.id),
                        ('budget_id.state', '=', 'done'),('budget_id.start_date','<=',today_date),('budget_id.end_date','>=',today_date)  # Only check against approved budgets
                    ])
                    if budget_lines:
                        total_remaining = sum(budget_lines.mapped('remaining_quantity'))
                        if line.product_qty > total_remaining:
                            raise ValidationError(
                                _("Quantity for product %s exceeds available budget at location %s. Requested: %s, Available: %s") %
                                (line.product_id.display_name,
                                 line.request_id.picking_type_id.default_location_dest_id.display_name, line.product_qty,
                                 total_remaining)
                            )
    
                        budget_lines.write({
                            'ordered_quantity': budget_lines.ordered_quantity + line.product_qty
                        })
    
                    else:
                        raise ValidationError(_(
                            "Product %s doesn't have any budget allocated at location %s. Department %s. "
                        )
                                              % (line.product_id.display_name, line.request_id.picking_type_id.default_location_dest_id.display_name,
                                                 line.request_id.stock_depart.name)
                                            )


    def button_rejected(self):
        for req in self:
            for line in req.line_ids:
                dest_location = line.request_id.picking_type_id.default_location_dest_id
                budget_lines = self.env['quantity.budget.line'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', dest_location.id),
                    ('budget_id.department_id', '=', line.request_id.stock_depart.id),
                    ('budget_id.state', '=', 'done'),('budget_id.start_date','<=',req.date_start),('budget_id.end_date','>=',req.date_start)  # Only check against approved budgets
                ])
                if budget_lines:
                    budget_lines.write({
                        'ordered_quantity': budget_lines.ordered_quantity - line.product_qty
                    })

        self.mapped("line_ids").do_cancel()
        return self.write({"state": "rejected"})


# class PurchaseRequestLine(models.Model):
#     _inherit = 'purchase.request.line'

#     @api.constrains('product_id', 'request_id')
#     def _check_product_budget_location(self):
#         logger.info('starttttttttttttttttttttttttttttttt')
#         logger.info('starttttttttttttttttttttttttttttttt')
#         logger.info('starttttttttttttttttttttttttttttttt')
#         logger.info('starttttttttttttttttttttttttttttttt')
#         logger.info('starttttttttttttttttttttttttttttttt')
#         logger.info('starttttttttttttttttttttttttttttttt')
#         for line in self:
#             if not line.product_id or not line.request_id:
#                 continue

#             pr_location = line.request_id.picking_type_id.default_location_dest_id
#             logger.info(pr_location)
#             budget_lines = self.env['quantity.budget.line'].search([
#                 ('product_id', '=', line.product_id.id),
#                 ('budget_id.state', '=', 'done')
#             ])
#             logger.info(budget_lines)

#             if budget_lines:
#                 # Check if any budget line exists for this product but with different location
#                 matching_location = False
#                 for budget_line in budget_lines:
#                     if budget_line.location_id == pr_location:
#                         matching_location = True
#                         break

#                 if not matching_location:
#                     raise ValidationError(_(
#                         "Product %s doesn't have any budget allocated for location %s. "
#                         "Please select a product with budget for this location or change the PR location."
#                     )
#                         % (line.product_id.display_name, pr_location.name)
#                     )
#                 logger.info('enddddddddddddddddddddddddddddddddddddd')
#                 logger.info('enddddddddddddddddddddddddddddddddddddd')
#                 logger.info('enddddddddddddddddddddddddddddddddddddd')
#                 logger.info('enddddddddddddddddddddddddddddddddddddd')
#                 logger.info('enddddddddddddddddddddddddddddddddddddd')
