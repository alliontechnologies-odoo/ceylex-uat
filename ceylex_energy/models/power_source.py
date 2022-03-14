from odoo import fields, models, api, _


class PowerSource(models.Model):
    _name = 'power.source'
    _description = "Power Source"

    name = fields.Char(required=True)
    energy_input_ids = fields.Many2many('energy.input', 'energy_input_power_rel', 'source_id', 'input_id', string="Input Lines")
    # energy_result_ids = fields.One2many('power.source.result', 'energy_result_power_rel', 'source_id', 'input_id', string="Result Lines")
    energy_result_ids = fields.One2many('power.source.result', 'power_source_id', string="Result Lines")


class PowerSourceResults(models.Model):
    _name = 'power.source.result'
    _description = 'Power Source Result'

    name = fields.Char(string="Title", required=True)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    code = fields.Text(string="Formula", help="""
        Write functions using input code
        If you want company values - company
        if you want current record value - record
    
    """)
    power_source_id = fields.Many2one('power.source', string="Power Source")

