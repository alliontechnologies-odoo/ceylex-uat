from odoo import api, fields, models, Command, _
from odoo.exceptions import ValidationError
from odoo.http import request

MONTH_LIST=[
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]

class AccountMove(models.Model):
    _inherit = "account.move"

    _sql_constraints = [
        ('vendor_ref_unique', 'unique(ref)', 'Duplicate Reference Number Found')
    ]

    def compute_meter_reading(self):
        """calculate count of meters"""
        for rec in self:
            meters = self.env['meter.reading'].search([('invoice_id', '=', rec.id)])
            if meters:
                rec.meter_reading = len(meters)
                if not self.energy_invoice:
                    self.energy_invoice = True
            else:
                rec.meter_reading = 0
                if self.energy_invoice:
                    self.energy_invoice = False

    def _get_years(self):
        """get list of years from 2009 """
        return [(str(i), i) for i in range(fields.Date.today().year, fields.Date.today().year - 11, -1)]

    meter_reading = fields.Integer(compute="compute_meter_reading")
    energy_invoice = fields.Boolean(default=False, store=True)
    year = fields.Selection(
        selection='_get_years', string='Year', required=True,
        default=lambda x: str(fields.Date.today().year))
    month = fields.Selection(MONTH_LIST, required=True, default=lambda self: str(fields.Date.today().month))
    submitted_date = fields.Date(string='Submitted Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})

    @api.onchange('invoice_date')
    def onchange_submitted_date(self):
        """
        Set invoice date as a submitted date
        """
        if not self.submitted_date and self.invoice_date:
            self.submitted_date = self.invoice_date


    @api.model
    def create(self, vals):
        """
        Overwrite create method and add ref number to uppercase to unique ref
        """
        if vals.get('ref'):
            vals['ref'] = vals.get('ref').upper()
        res = super(AccountMove, self).create(vals)
        return res

    def action_meter_readings(self):
        """Return meter reading input view when click the button"""
        self.ensure_one()
        return {
            'name': _('Meter Readings'),
            'type': 'ir.actions.act_window',
            'res_model': 'meter.reading',
            'view_mode': 'tree,form',
            'domain': [('invoice_id', '=', self.id)],
        }

