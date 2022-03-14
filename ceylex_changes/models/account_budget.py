from odoo import api, fields, models


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"
    _description = "Budget Line"

    committed_expenditure = fields.Monetary(string='Committed Expenditure',compute="compute_committed_expenditure", help="Amount really earned from purchase order")

    def compute_committed_expenditure(self):
        """Calculate committed_expenditure from non invoice purchase order line analytic account"""
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                purchase_lines = self.env['purchase.order.line'].search([
                    ('account_analytic_id', '=', line.analytic_account_id.id),
                    ('date_order', '>=', date_from),
                    ('date_order', '<=', date_to),
                    ('state', '=', 'purchase'),
                    ('invoice_lines', '=', False),
                ])
                total = 0.00
                for order in purchase_lines:
                    total += order.price_subtotal
                line.committed_expenditure = total
            else:
                line.committed_expenditure = 0.00


