from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
from odoo.addons.ceylex_changes.models.account_move import MONTH_LIST
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta


class EnergyCalculation(models.Model):
    _name = 'energy.calculation'
    _description = 'Energy Calculation'

    def _get_years(self):
        """get list of years from 2009 """
        return [(str(i), i) for i in range(fields.Date.today().year, fields.Date.today().year - 11, -1)]

    name = fields.Char(default="New", compute="compute_name", store=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    installed_capacity = fields.Float(string="Installed Capacity(MW)", default=0.00)
    hours_in_day = fields.Float(default=0.00, string="Hours In a Day")
    operational_period = fields.Float(default=0.00, string="Operational Period(days)", compute="compute_operational_period")
    power_source_id = fields.Many2one('power.source', string="Power Source", required=True)
    calculations_input_ids = fields.One2many('energy.calculation.input', 'calculations_id', string="Input Lines")
    calculations_result_ids = fields.One2many('energy.calculation.result', 'calculations_id', string="Result Lines")
    total_hours = fields.Float(default=0.00, compute="compute_operational_period")
    summery = fields.Text(string="Plant operation summary for the  month")
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'confirmed')], default='draft')

    year = fields.Selection(
        selection='_get_years', string='Year', required=True,
        default=lambda x: str(fields.Date.today().year))
    month = fields.Selection(MONTH_LIST, required=True, default=lambda self: str(fields.Date.today().month))

    _sql_constraints = [
        ('company_date_uniq', 'unique (company_id, start_date, end_date)', 'Company with date range should be unique!')]

    @api.depends('start_date','end_date')
    def compute_name(self):
        """Generste record name from date and company"""
        for rec in self:
            if rec.company_id and rec.start_date and rec.end_date:
                rec.name = "%(company)s - From %(start_date)s To %(end_date)s" % {'company': rec.company_id.name, 'start_date':rec.start_date, 'end_date': rec.end_date}
            else:
                rec.name = "New"

    @api.depends('start_date','end_date','hours_in_day')
    def compute_operational_period(self):
        """Compute Operational period"""
        for rec in self:
            if rec.start_date and rec.end_date:
                no_of_days = (rec.end_date-rec.start_date).days
                rec.operational_period = no_of_days
                if rec.hours_in_day > 0.00:
                    rec.total_hours = rec.hours_in_day * no_of_days
                else:
                    rec.total_hours = 0.00
            else:
                rec.operational_period = 0.00
                rec.total_hours = 0.00

    @api.onchange('company_id')
    def onchange_company_id(self):
        """Onchange company ID"""
        self.installed_capacity = self.company_id.installed_capacity
        self.power_source_id = self.company_id.power_source_id.id

    @api.onchange('month', 'year')
    def onchange_month_year(self):
        """get date range when Onchange month and year"""
        if self.month and self.year:
            first_day = datetime.strptime('01-%s-%s' %(str(self.month), str(self.year)), '%d-%m-%Y')
            end = first_day + relativedelta(months=1) - timedelta(days=1)
            self.start_date = first_day
            self.end_date = end


    def get_input_lines(self):
        """Get input lines from power source when click the button"""
        input_lines = []
        for lines in self.power_source_id.energy_input_ids:
            input = self.calculations_input_ids.create({
                'calculations_input_ids': lines.id
            })
            input_lines.append(input.id)
        self.write({
            'calculations_input_ids': [(6, 0, input_lines)]
        })

    def get_result_lines(self):
        """Get result lines from power source when click the 'get results' button"""
        input_vals = {  # list of variables
            'amount': 0.00,
            'company': self.company_id,
            'record': self,
        }
        for lines in self.calculations_input_ids:
            input_vals[lines.code] = lines.amount

        results_vals = []

        for source in self.power_source_id.energy_result_ids:
            input_vals['amount'] = 0.00
            #   create result lines
            source_id = self.create_calculations_result_ids(source, input_vals)
            results_vals.append(source_id.id)

        self.write({
            'calculations_result_ids': [(6, 0, results_vals)]
        })

    def create_calculations_result_ids(self, source, input_vals):
        """Get amounts from calculations"""
        datadict = input_vals
        try:
            if source.code:
                #   run result formula
                safe_eval(source.code, datadict, mode="exec", nocopy=True)
            result = self.env['energy.calculation.result'].create({
                'name': source.name,
                'uom_id': source.uom_id.id,
                'amount': datadict.get('amount', False)
            })
            return result
        except Exception as e:
            raise ValidationError(_("Wrong formula code defined or wrong input type for( %s )" % source.code))

    def button_confirm(self):
        """Functions for button confirm"""
        self.ensure_one()
        if self.state == "draft":
            self.write({
                'state': 'confirmed'
            })

    def button_set_to_draft(self):
        """Functions for button set to draft"""
        self.ensure_one()
        if self.state == "confirmed":
            self.write({
                'state': 'draft'
            })




class EnergyCalculationInputs(models.Model):
    _name = 'energy.calculation.input'
    _description = 'Energy Calculation Input'

    calculations_input_ids = fields.Many2one('energy.input', string="Input Lines")
    code = fields.Char(string="Code", related="calculations_input_ids.code")
    uom_id = fields.Many2one('uom.uom', string="Unit of Measures", related="calculations_input_ids.uom_id")
    amount = fields.Float(default=0.00)
    calculations_id = fields.Many2one('energy.calculation')


class EnergyCalculationResults(models.Model):
    _name = 'energy.calculation.result'
    _description = 'Energy Calculation Result'

    name = fields.Char()
    uom_id = fields.Many2one('uom.uom', string="Unit of Measures")
    amount = fields.Float(default=0.00, string="Value")
    calculations_id = fields.Many2one('energy.calculation')
