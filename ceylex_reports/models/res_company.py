from odoo import api, fields, models, SUPERUSER_ID, _

from odoo.http import request
from datetime import datetime, date


class ResCompany(models.Model):
    _inherit = "res.company"

    fax = fields.Char()
    company_short_code = fields.Char(string="Supplier rating sequence ", size=12, help="Maximum 12 digits")
    company_short_seq = fields.Many2one('ir.sequence')
    invoice_footer = fields.Image("Special Invoice Footer Image", max_width=1920, max_height=1920)
