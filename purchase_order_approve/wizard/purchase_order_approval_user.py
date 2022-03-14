from odoo import fields, models, api
from datetime import datetime
from datetime import timedelta


class POApprovalUserWizard(models.TransientModel):
    _name = 'po.approval.user.wizard'
    _description= "Purchase order approval user Wizard"

    user_id = fields.Many2one('res.users', string="Approver", required=1, domain=lambda self: [('groups_id', 'in', self.env.ref('purchase_order_approve.group_po_approval_security').id)])
    model_id = fields.Many2one('ir.model')
    record_id = fields.Integer()

    def approval_submission(self):
        """action for submit wizard data and send email after approve """
        template_id = self.env.ref('purchase_order_approve.mail_template_for_po_approval')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web?login/#id=' + str(self._context.get('active_id')) + '&view_type=form&model=' + str(self._context.get('active_model'))
        record = self.env[str(self._context.get('active_model'))].search([('id', '=', self.record_id)], limit=1)
        record.write({
            'custom_url': url,
            'state': 'awaiting_approval',
        })
        context = self.env.context.get('mail_body')
        context['mail_to'] = self.user_id.email
        context['custom_url'] = url
        self.env['mail.template'].browse(template_id.id).with_context(context).send_mail(self.id, True)
