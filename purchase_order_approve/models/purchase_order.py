from odoo import api, fields, models, SUPERUSER_ID, _

from odoo.http import request
from datetime import datetime, date

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    approved_by = fields.Many2one('res.users', string="Approved/Rejected By", readonly=1, tracking=True)
    approve_Date = fields.Date(string="Approved/Rejected Date", readonly=1, tracking=True)
    comment = fields.Text(string="Approved/Rejected Comment", readonly=1, tracking=True)
    custom_url = fields.Char("URL")
    state = fields.Selection(selection_add=[
        ('awaiting_approval', 'Awaiting Approval'),
        ('approved', 'Approved'),
    ])

    # function for sent for approval
    def sent_to_approval(self):
        model = self.env['ir.model'].search([('model', '=', request.params.get('model'))])
        mail_body = {
            'subject': ' Request approval of %s' % self.name,
            'msg_type': 'There is a pending purchase order for your approval. Please do the needful.',

        }
        return {
            'name': _('Request approval'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'po.approval.user.wizard',
            'target': 'new',
            'context': {
                'default_model_id': model.id,
                'default_record_id': self.id,
                'mail_body': mail_body,
            }
        }

    # function for approved comment
    def po_approved(self):
        model = self.env['ir.model'].search([('model', '=', request.params.get('model'))])
        mail_body = {
            'subject': '  %s has been approved' % self.name,
            'msg_type': 'The Purchase Order %s has been approved. You can proceed.' % self.name,
        }
        return {
            'name': _('Approve'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order.approve.reject.comment.wizard',
            'target': 'new',
            'context': {
                'default_model_id': model.id,
                'default_record_id': self.id,
                'default_action': 'Approved',
                'mail_body': mail_body,
            }
        }

    # function for refection
    def po_reject(self):
        model = self.env['ir.model'].search([('model', '=', request.params.get('model'))])

        mail_body = {
            'subject': '  %s has been rejected' % self.name,
            'msg_type': 'The Purchase Order %s has been rejected.' % self.name,
        }
        return {
            'name': _('Reject'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order.approve.reject.comment.wizard',
            'target': 'new',
            'context': {
                'default_model_id': model.id,
                'default_record_id': self.id,
                'default_action': 'Rejected',
                'mail_body': mail_body,
            }
        }

    # Button action for confirm purchase order
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'approved']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True