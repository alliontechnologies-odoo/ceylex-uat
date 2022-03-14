from odoo import fields, models, api
from datetime import datetime
from datetime import timedelta


class PurchaseOrderApproveRejectCommentWizard(models.TransientModel):
    _name = 'purchase.order.approve.reject.comment.wizard'
    _description = "Purchase order Reject user Wizard"

    comment = fields.Text(string="Approve/Reject Comment")
    model_id = fields.Many2one('ir.model')
    record_id = fields.Integer()
    action = fields.Char(string="Action")

    def submission(self):
        """action for submit wizard data and send email after reject """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web?login/#id=' + str(self._context.get('active_id')) + '&view_type=form&model=' + str(
            self._context.get('active_model'))
        record = self.env[str(self._context.get('active_model'))].search([('id', '=', self.record_id)], limit=1)
        context = self.env.context.get('mail_body')

        if self.action == 'Approved':
            template_id = self.env.ref('purchase_order_approve.mail_template_for_approve_purchase_order')
            record.write({
                'custom_url': url,
                'state': 'approved',
                'approved_by': self._uid,
                'approve_Date': datetime.today().date(),
                'comment': self.comment,
            })
            context['mail_to'] = record.user_id.email
            context['custom_url'] = url
            context['user'] = record.user_id.display_name
            self.env['mail.template'].browse(template_id.id).with_context(context).send_mail(self.id, True)

        if self.action == 'Rejected':
            template_id = self.env.ref('purchase_order_approve.mail_template_for_reject_purchase_order')
            record.write({
                'custom_url': url,
                'state': 'cancel',
                'approved_by': self._uid,
                'approve_Date': datetime.today().date(),
                'comment': self.comment,
            })
            context['mail_to'] = record.user_id.email
            context['custom_url'] = url
            context['user'] = record.user_id.display_name
            self.env['mail.template'].browse(template_id.id).with_context(context).send_mail(self.id, True)




