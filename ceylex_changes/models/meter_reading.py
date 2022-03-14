from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError, ValidationError

class MeterReading(models.Model):
    _name = "meter.reading"
    _description = "Meter Reading"

    @api.model
    def default_get(self, default_fields):
        """Get meter input types when loading"""
        values = super().default_get(default_fields)
        meter_lines =[
            (0, 0, {'day_type': self.env.ref('ceylex_changes.meter_input_type_day').id}),
            (0, 0, {'day_type': self.env.ref('ceylex_changes.meter_input_type_peak').id}),
            (0, 0, {'day_type': self.env.ref('ceylex_changes.meter_input_type_off_peak').id})
        ]
        values['meter_line_ids'] = meter_lines
        return values

    name = fields.Char(default=lambda self: _("New"), store=True, compute="compute_name")
    date = fields.Date(default=fields.Date.today)
    meter_no = fields.Char(string="Meter Number", required=True)
    present_date = fields.Date(string="Present Reading ", default=fields.Date.today)
    previous_date = fields.Date(string="Previous Reading ", default=lambda x: fields.Date.today() - relativedelta(months=1))
    no_units_delivered = fields.Float(string="Number of units delivered ", default=0.00, compute="compute_total_amount")
    current_tariff = fields.Float(string="Current Tariff", default=0.00)
    delivered_value = fields.Float(string="Value of Energy delivered", default=0.00, compute="compute_total_amount")
    tax_ids = fields.Many2one(
        comodel_name='account.tax',
        string="Taxes",
        context={'active_test': False},
        check_company=True,
        help="Taxes that apply on the base amount")
    vat = fields.Float(string="VAT Amount", default=0.00)
    total_amount = fields.Float(string="Total Amount", default=0.00, compute="compute_total_amount")
    meter_line_ids = fields.One2many('meter.reading.lines', 'meter_id', string="Readings")
    invoice_id = fields.Many2one('account.move')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Company Currency', readonly=True, default=lambda self: self.env.company.currency_id.id)

    @api.depends('meter_no','date')
    def compute_name(self):
        """Generate name using meter no and date"""
        for rec in self:
            rec.name = "%s - ( %s)" % (str(rec.meter_no)if rec.meter_no else "New", str(rec.date))

    @api.depends('meter_line_ids', 'current_tariff', 'tax_ids')
    def compute_total_amount(self):
        """Compute amounts """
        for rec in self:
            no_units_delivered = 0.00
            for units in rec.meter_line_ids:
                no_units_delivered += units.energy
            delivered_value = no_units_delivered * rec.current_tariff

            rec.no_units_delivered = no_units_delivered
            rec.delivered_value = delivered_value
            rec.total_amount = delivered_value
            if rec.tax_ids:
                tax_details = rec.tax_ids.compute_all(price_unit=delivered_value, currency=rec.currency_id)
                rec.vat = tax_details['total_included'] - tax_details['total_excluded']
                rec.total_amount = tax_details['total_included']

    def button_update_invoice(self):
        """Add invoice line to relevant invoice"""
        self.ensure_one()
        if self.invoice_id:
            self.invoice_id.write({
                'invoice_line_ids': [(0, 0, {'name': self.name, 'price_unit': self.delivered_value, 'tax_ids': [(4, self.tax_ids.id)] if self.tax_ids.id else False})]
            })

    def unlink(self):
        """check related invoice is posted or not"""
        if self.invoice_id.state == "posted":
            raise ValidationError("Related Invoice has Posted")
        return super(MeterReading, self).unlink()

    def write(self, vals):
        """check related invoice is posted or not"""
        res = super(MeterReading, self).write(vals)
        if self.invoice_id.state == "posted":
            raise ValidationError("Invoice has Posted")
        return res


class MeterReadingLines(models.Model):
    _name = "meter.reading.lines"
    _description = "Meter Reading Lines"

    day_type = fields.Many2one('meter.reading.types')
    present = fields.Integer(default=000000, string="Present Reading")
    previous = fields.Integer(default=000000, string="Previous Reading")
    mf = fields.Integer(default=0.00, string="MF")
    energy = fields.Float(string="Energy Sent (kWh)", default=0.00, compute="compute_energy", store=True)
    meter_id = fields.Many2one('meter.reading')

    @api.depends('present', 'previous')
    def compute_energy(self):
        """ Compute and get difference of meter readings"""
        for rec in self:
            rec.energy = rec.present - rec.previous


class MeterReadingTypes(models.Model):
    _name = "meter.reading.types"
    _description = "Meter Reading Types"

    name = fields.Char()

