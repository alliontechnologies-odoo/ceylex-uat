# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields 


class AccountJournal(models.Model):
    _inherit = "account.journal"

    custom_approval_type = fields.Selection(
    	[
    	('no_approval', 'No Approval'),
    	('second_level_approval', 'Second Level Approval'),
        ('both', 'Second and Third Level Approval')
    	],
    	string='Approval Type', 
        default='no_approval',
    	readonly=False
    )
    custom_second_approver_ids = fields.Many2many(
        'res.users',
        relation='account_move_second_approval_rel',
        string='Second Approvers', 
        copy=False,
        domain=lambda self: [
            ('groups_id', 'in', self.env.ref('odoo_invoice_triple_approval.group_account_journal_entry_security').id)]
    )
    custom_third_approver_ids = fields.Many2many(
        'res.users',
        string='Third Approvers', 
        copy=False,
        domain=lambda self: [
            ('groups_id', 'in', self.env.ref('odoo_invoice_triple_approval.group_account_journal_entry_security').id)]
    )
    