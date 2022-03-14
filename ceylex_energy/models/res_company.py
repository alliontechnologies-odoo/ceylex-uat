from odoo import fields, models, api, _


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    vat = fields.Char(related='partner_id.vat', string="TIN No", readonly=False)
    power_source_id = fields.Many2one('power.source', string="Power Source", required=True)
    installed_capacity = fields.Float(string="Installed Capacity(MW)", default=0.00)
    temperature_coefficient = fields.Float(string="Temperature Coefficient(%/°C)", default=0.00)
    project_start_date = fields.Date(default=fields.Date.today)
    project_end_date = fields.Date(default=fields.Date.today)
    commercial_opr_start_date = fields.Date(default=fields.Date.today, string="Commercial Operation Start Date")

