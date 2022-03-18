from odoo import api, fields, models, SUPERUSER_ID, _

from odoo.http import request
from datetime import datetime, date
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    delivery_period = fields.Many2one('purchase.delivery.period', string="Delivery Period")
    delivery_term = fields.Many2one('purchase.delivery.term', string="Delivery Terms")
    quote_date = fields.Date(default=fields.Date.today)
    project_name = fields.Char()
    company_contact_ids = fields.Many2many('res.partner', 'company_contact_re_partner_rel', 'contact_id', 'order_id',
                                           domain="[('parent_id', '=', company_id)]")
    supplier_contact_id = fields.Many2one('res.partner', domain="[('parent_id', '=', partner_id)]")
    terms_and_condition_id = fields.Many2one('purchase.order.agreements')
    terms_and_condition_text = fields.Html(string="Description")

    @api.onchange('terms_and_condition_id')
    def onchange_terms_and_condition_id(self):
        """Get terms and conditions when change the selections"""
        if self.terms_and_condition_id:
            self.terms_and_condition_text = self.terms_and_condition_id.description

    def button_confirm(self):
        """Check is there a pending evaluation for this vendor"""
        if self.partner_id.is_rating_supplier and self.partner_id.pending_evaluation:
            raise ValidationError("Supplier evaluation is pending. Please complete the evaluation to proceed")
        return super(PurchaseOrder, self).button_confirm()


class PurchaseDeliveryPeriod(models.Model):
    _name = "purchase.delivery.period"
    _description = "purchase order Delivery period"

    name = fields.Char(string="Description", required=True)


class PurchaseDeliveryTerm(models.Model):
    _name = "purchase.delivery.term"
    _description = "purchase order Delivery Terms"

    name = fields.Char(string="Description", required=True)


class PurchaseOrderAgreements(models.Model):
    _name = "purchase.order.agreements"
    _description = "purchase order Agreements"

    name = fields.Char(string="Title", required=True)
    description = fields.Html(required=True)


