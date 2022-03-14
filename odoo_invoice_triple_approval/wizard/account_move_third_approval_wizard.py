# -*- coding: utf-8 -*-

import datetime

from odoo import models, fields , api , _
from odoo.exceptions import UserError


class AccountMoveThirdApprovalNotifyWizard(models.TransientModel):
    _name = 'custom.account.move.third.approval.wizard'
    _description = 'custom.account.move.third.approval.wizard'

    custom_third_approval_notify_id = fields.Many2one(
        'res.users',
        string='Third Approval Responsible',
        copy=False,
    )
    move_id = fields.Many2one(
        'account.move',
        string="Move",
        readonly=True
    )
    is_custom_third_approval_readonlty = fields.Boolean(
        'Is Custom Readonly?',
        copy=False,
    )

    @api.model
    def default_get(self, default_fields):
        """load invoices when load the record"""
        res = super(AccountMoveThirdApprovalNotifyWizard,self).default_get(default_fields)
        res['move_id'] = self.env['account.move'].browse(int(self._context.get('active_id'))).id
        return res

    @api.onchange('move_id')
    def onchange_move_id(self):
        """load third level approval"""
        domain = {}
        if self.move_id:
            domain = {'custom_third_approval_notify_id': [('id', 'in', self.move_id.journal_id.custom_third_approver_ids.ids)]}
        if self.move_id.custom_approval_type == 'second_level_approval':
            self.write({'is_custom_third_approval_readonlty': True})
        return {'domain': domain}

    def action_account_move_third_approval_notify(self):
        """send third level approval notification mails"""
        move_id = self.env['account.move'
        ].browse(self._context.get('active_ids'))
        state_list = {
            'entry': 'Journal Entry',
            'out_invoice': 'Customer Invoice',
            'out_refund': 'Customer Credit Note',
            'in_invoice': 'Vendor Bill',
            'in_refund': 'Vendor Credit Note',
            'out_receipt': 'Sales Receipt',
            'in_receipt': 'Purchase Receipt',
        }
        ctx = self._context.copy()
        state_list = dict(state_list)
        ctx.update({
            'state_list': state_list.get(move_id.move_type)
        })
        if move_id.custom_approval_type == 'second_level_approval' and self.env.uid not in move_id.journal_id.custom_second_approver_ids.ids:
            raise UserError(_('You are not allowed to Approve.'))
        if move_id.custom_approval_type == 'second_level_approval':
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
            move_id.write({
                'custom_url': url,
                'custom_is_second_level_approval': True,
                'custom_is_second_level_approver_id': self.env.uid,
                'custom_second_level_approval_date': datetime.datetime.now(),
                'custom_is_refuse_ribbon' : False
            })
            if move_id.move_type == 'out_invoice' or move_id.move_type == 'out_refund':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.email_template_final_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
            if move_id.move_type == 'entry':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.journal_entry_email_template_final_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
            if move_id.move_type == 'in_invoice' or move_id.move_type == 'in_refund':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.vendor_bill_email_template_final_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
            if move_id.move_type == 'out_receipt':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.sales_receipt_email_template_final_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
            if move_id.move_type == 'in_receipt':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.purchase_receipt_email_template_final_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
        if move_id.custom_approval_type == 'both' and self.env.uid not in move_id.journal_id.custom_second_approver_ids.ids:
            raise UserError(_('You are not allowed to approve.'))
        if move_id.custom_approval_type == 'both':
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
            move_id.write({
                'custom_url': url,
                'custom_is_second_level_approval': True,
                'custom_is_second_level_approver_id': self.env.uid,
                'custom_second_level_approval_date': datetime.datetime.now(),
                'custom_third_approval_notify_id' : self.custom_third_approval_notify_id,
                'custom_is_refuse_ribbon' : False
            })
            if move_id.move_type == 'out_invoice' or move_id.move_type == 'out_refund':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.email_template_third_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
            if move_id.move_type == 'entry':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.journal_entry_email_template_third_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
            if move_id.move_type == 'in_invoice' or move_id.move_type == 'in_refund':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.vendor_bill_email_template_third_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
            if move_id.move_type == 'out_receipt':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.sales_receipt_email_template_third_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
            if move_id.move_type == 'in_receipt':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web?login/#id=' + str(move_id.id) + '&view_type=form&model=account.move'
                move_id.write({
                    'custom_url': url,
                })
                template = self.env.ref('odoo_invoice_triple_approval.purchase_receipt_email_template_third_approval_custom_probc')
                template.sudo().with_context(ctx).send_mail(move_id.id)
                move_id.write({
                    'is_custom_send_mail':True
                })
        return True
