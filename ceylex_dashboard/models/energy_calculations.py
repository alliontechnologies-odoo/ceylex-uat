from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
from odoo.addons.ceylex_changes.models.account_move import MONTH_LIST

class EnergyCalculation(models.Model):
    _inherit = 'energy.calculation'
    _description = 'Energy Calculation'

    @api.model
    def get_power_generated_summery(self, start_date=False, end_date=False):
        """Get power generated summery from energy calculations to dashboard

        -> Search all energy calculations
        -> created separated company with values
        -> find Calculated Energy from calculations results line
        -> find all plant factor and return

        𝑃𝑙𝑎𝑛𝑡 𝐹𝑎𝑐𝑡𝑜𝑟 (%) = 𝐸𝑛𝑒𝑟𝑔𝑦 𝑒𝑥𝑝𝑜𝑟𝑡𝑒𝑑 𝑡𝑜 𝑔𝑟𝑖𝑑 / (𝑃𝑙𝑎𝑛𝑡 𝑐𝑎𝑝𝑎𝑐𝑖𝑡𝑦 × 𝑇𝑜𝑡𝑎𝑙 𝐻𝑜𝑢𝑟𝑠) × 100


        """
        if start_date and end_date:
            calculations = self.search([('start_date', '>=', start_date), ('end_date', '<=', end_date)], order='company_id desc, year asc, month desc')
        else:
            calculations = self.search([], order='company_id desc, year asc, month desc')
        power = []
        company =[]
        for calculation in calculations:
            if calculation.company_id.id not in company:
                vals={
                    'company': calculation.company_id.name,
                    'power': 0.00,
                    'capacity': calculation.company_id.installed_capacity,
                    'plant_factor': 0.00,
                    'total_hours': calculation.total_hours,
                    'period': MONTH_LIST[int(calculation.month)-1][1]
                }
                company.append(calculation.company_id.id)
                power.append(vals)
            index = company.index(calculation.company_id.id)
            for line in calculation.calculations_result_ids:
                com_power = 0.00
                plant_factor = 0.00
                if line.name == "Energy exported to the grid":
                    com_power = line.amount
                if calculation.name == "Plant Factor":
                    plant_factor = line.amount
                power[index].update({
                    'power': power[index]['power'] + com_power,
                    'plant_factor':  power[index]['plant_factor']+ plant_factor,
                    'period': MONTH_LIST[int(calculation.month)-1][1] + " " + power[index]['period'] if MONTH_LIST[int(calculation.month)-1][1] not in power[index]['period'] else power[index]['period']
                })

        # Update plant Factor
        for line in power:
            if line['power'] > 0 and line['capacity'] > 0 and line['total_hours']:
                plant_factor = (line['power'] / (line['capacity'] * line['total_hours'])) * 100
            else:
                plant_factor = 0.00
            line['plant_factor'] = f"{plant_factor:,.2f}"
        return {'power': power}