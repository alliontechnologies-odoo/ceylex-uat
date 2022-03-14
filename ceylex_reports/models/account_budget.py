
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountBudgetPost(models.Model):
    _inherit = "account.budget.post"

    def _check_account_ids(self, vals):
        """
        # Raise an error to prevent the account.budget.post to have not specified account_ids.
        # This check is done on create because require=True doesn't work on Many2many fields.
        # Inherit and remove account Validation
        """
        if 'account_ids' in vals:
            account_ids = self.new({'account_ids': vals['account_ids']}, origin=self).account_ids
        else:
            account_ids = self.account_ids

        parent_id = True
        if not vals.get('parent_id'):
            parent_id = False
        if not account_ids and parent_id:
            raise ValidationError(_('The budget must have at least one account.'))

    parent_id = fields.Many2one('account.budget.post', string="Parent Budget", domain="[('parent_id','=',False)]")


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    uom_id = fields.Many2one('uom.uom', string="Unit")
    quantity = fields.Float(string="Quantity", default=0.00)
    unit_price = fields.Float(string="Unit Price", default=0.00)
    remarks = fields.Char(string="Remarks")