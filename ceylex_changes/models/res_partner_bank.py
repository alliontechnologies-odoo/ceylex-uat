from odoo import api, fields, models, _


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    branch_name = fields.Char(string="Branch Name")
