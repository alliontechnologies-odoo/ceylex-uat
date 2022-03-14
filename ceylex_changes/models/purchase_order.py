from odoo import api, fields, models, SUPERUSER_ID, _

from odoo.http import request
from datetime import datetime, date


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    vendor_industry = fields.Many2one('res.partner.industry', string="Vendor Industry", copy=False)

    @api.onchange('vendor_industry')
    def onchange_vendor_industry(self):
        """Add filter to partner when change the industry of vendor"""
        company_id = self.company_id.id
        if self.vendor_industry:
            domain = {'domain': {'partner_id': [('industry_id', '=', self.vendor_industry.id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]}}
        else:
            domain = {'domain': {
                'partner_id': ['|', ('company_id', '=', False), ('company_id', '=', company_id)]}}
        return domain
