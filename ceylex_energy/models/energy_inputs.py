from odoo import fields, models, api, _


class EnergyInput(models.Model):
    _name = 'energy.input'
    _description = 'Energy Input'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    uom_id = fields.Many2one('uom.uom')
    active = fields.Boolean(default=True)
