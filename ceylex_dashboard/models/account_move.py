import datetime
import calendar

from odoo import models, fields, api
from odoo.tools import date_utils
from odoo.http import request

from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.addons.ceylex_changes.models.account_move import MONTH_LIST

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def get_energy_delivered_to_national_grid(self, start_date=None, end_date=None):
        """Energy delivered to national grid calculated from invoice"""

        today = datetime.strptime(end_date, '%Y-%m-%d') if end_date else fields.date.today()
        session_user_id = self.env.uid
        before_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else today - relativedelta(months=5)
        self._cr.execute('''select invoice.move_type, invoice.id, invoice.name, invoice.month, 
        invoice.year, invoice.amount_total_signed, invoice.submitted_date, invoice.company_id, company.name, invoice.amount_residual_signed 
        FROM account_move invoice, res_company company WHERE invoice.state = 'posted' AND invoice.move_type='out_invoice' AND invoice.energy_invoice=True 
        AND invoice.invoice_date >= '%s' AND invoice.invoice_date <= '%s'
        AND company.id = invoice.company_id order by company_id''' % (before_date, today))

        data = self._cr.fetchall()
        energy = []
        company = []
        for rec in data:
            if rec[7] not in company:
                # if not already saved company
                energy.append({
                    'id': rec[7],
                    'name': rec[8],
                    'total': '0.00',
                    'record': []    # data order date month , submit date, value
                })
                company.append(rec[7])

            index = company.index(rec[7])
            energy[index]['record'].append({
                'month': MONTH_LIST[int(rec[3])-1][1] + "-" + rec[4],
                'date': rec[6],
                'value': f"{rec[5]:,.2f}"
            })
            total = float(energy[index]['total'].replace(',', ''))
            total += rec[5]
            energy[index]['total'] = f"{total:,.2f}"

        return {'energy': energy}





