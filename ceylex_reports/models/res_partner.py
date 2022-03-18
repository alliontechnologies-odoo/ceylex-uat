from odoo import api, fields, models
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase
from datetime import timedelta
from odoo.exceptions import AccessError, UserError, ValidationError


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    is_rating_supplier = fields.Boolean(string="Rating Supplier", default=False, copy=False)
    evaluation_repeat = fields.Integer(string="Repeat: No of Days", default=30)
    next_evaluation_date = fields.Date(default=lambda x: fields.Date.today() + timedelta(days=x.evaluation_repeat))
    pending_evaluation = fields.Boolean(default=False)

    @api.onchange('evaluation_repeat')
    def onchange_evaluation_repeat(self):
        """Calculate next evaluation date when change the no of days
           -> Is there any ratings
                next evaluation date = last evaluation date + no of days
           -> if not ratings yet
                next evaluation date = current date + no of days
        """
        if self.evaluation_repeat:
            ratings = self.env['supplier.rating'].search(
                [('partner_id', '=', self.id)], order="date desc", limit=1)
            if ratings:
                self.next_evaluation_date = ratings.date + timedelta(days=self.evaluation_repeat)
            else:
                self.next_evaluation_date = fields.Date.today() + timedelta(days=self.evaluation_repeat)

    def _check_is_there_pending_evaluations(self):
        """Check is there pending ratings to approve"""
        for rec in self.search([('is_rating_supplier', '=', True)]):
            today = fields.Date.today()
            if today > rec.next_evaluation_date:
                ratings = self.env['supplier.rating'].search(
                    [('partner_id', '=', rec.id), ('date', '>=', rec.next_evaluation_date), ('state', '=', 'approved',)], order="date desc", limit=1)
                if ratings:
                    rec.pending_evaluation = False
                else:
                    rec.pending_evaluation = True
            else:
                rec.pending_evaluation = True


class AccountPayment(models.Model):
    _inherit = "account.payment"
    """Inherit the class and add pending evaluation filter"""

    def action_post(self):
        """Block the payment when there is a pending vendor evaluations"""
        if self.partner_id.is_rating_supplier and self.partner_id.pending_evaluation:
            raise ValidationError("Supplier evaluation is pending. Please complete the evaluation to proceed")
        return super(AccountPayment, self).action_post()
