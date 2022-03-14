from odoo import api, fields, models
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from datetime import timedelta

class SupplierRating(models.Model):
    _name = 'supplier.rating'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Supplier Rating"

    @api.model
    def default_get(self, fields):
        """ Use active_ids from the context to fetch the leads/opps to merge.
            In order to get merged, these leads/opps can't be in 'Dead' or 'Closed'
        """
        result = super(SupplierRating, self).default_get(fields)
        result['line_ids'] = [
            # (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_technical_eval').id}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_technical_eval').id, 'description_id': self.env.ref('ceylex_reports.desc_prod_service').id, 'description': self.env.ref('ceylex_reports.desc_prod_service').name}),
            # (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_experience').id}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_experience').id, 'description_id': self.env.ref('ceylex_reports.desc_engineering').id, 'description': self.env.ref('ceylex_reports.desc_engineering').name}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_delivery').id}),
            # (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_quality').id}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_quality').id, 'description_id': self.env.ref('ceylex_reports.desc_iso9001').id, 'description': self.env.ref('ceylex_reports.desc_iso9001').name}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_quality').id, 'description_id': self.env.ref('ceylex_reports.desc_iso14001').id, 'description': self.env.ref('ceylex_reports.desc_iso14001').name}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_quality').id, 'description_id': self.env.ref('ceylex_reports.desc_iso45001').id, 'description': self.env.ref('ceylex_reports.desc_iso45001').name}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_market').id}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_payment').id}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_financial').id}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_price').id}),
            # (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_relationship').id}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_relationship').id, 'description_id': self.env.ref('ceylex_reports.desc_free_supply').id, 'description': self.env.ref('ceylex_reports.desc_free_supply').name}),
            (0, 0, {'category_id': self.env.ref('ceylex_reports.cat_relationship').id, 'description_id': self.env.ref('ceylex_reports.desc_on_time_delivery').id, 'description': self.env.ref('ceylex_reports.desc_on_time_delivery').name}),
        ]
        return result

    name = fields.Char(default=lambda self: 'Draft', copy=False, store=True,)
    partner_id = fields.Many2one('res.partner', tracking=True, required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    date = fields.Date(string="Evaluation Date", default=fields.Date.today(), required=True)
    approved_by = fields.Many2one('res.users', tracking=True,)
    approved_date = fields.Datetime(tracking=True)

    to_be_purchased = fields.Char(string="To be Purchased:")
    delivery = fields.Selection([('accept', 'Acceptable'), ('notAccept', 'Not Acceptable')], tracking=True, required=True, default='accept')
    technical_compliance = fields.Selection([('accept', 'Acceptable'), ('notAccept', 'Not Acceptable')], tracking=True, required=True, default='accept')

    # Capability Assessment
    line_ids = fields.One2many('supplier.rating.line', 'rating_id', tracking=True)
    total = fields.Integer(tracking=True, compute="compute_total")

    remarks = fields.Text(tracking=True)
    recommendation_committee = fields.Many2many('hr.employee', 'rating_employee_rel', 'employee_id', 'rating_id', tracking=True)
    revision_date = fields.Date(default=fields.Date.today(), tracking=True)
    revision_no = fields.Integer(default=00, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
        # ('cancel', 'Canceled'),
    ], string="Status", tracking=True, default='draft')

    def action_confirm(self):
        """Confirm the record and generate the sequence
            It will get sequence short code from company profile
            if it's not found it will take first four letters from company name
        """
        self.ensure_one()
        if self.name == "Draft":
            if not self.company_id.company_short_seq: # create a sequence
                new_sequence = self.env['ir.sequence'].create({
                    'name': 'supplier Rating',
                    'code': 'supplier.rating',
                    'company_id': self.company_id.id,
                    'prefix': self.company_id.company_short_code.replace(' ', '') + "/" if self.company_id.company_short_code else self.company_id.name[0:4].replace(' ', '') + "/",
                    'padding': 5,
                    'number_next': 1,
                    'number_increment': 1
                })
                self.company_id.write({
                    "company_short_seq": new_sequence.id
                })

            self.name = self.env['ir.sequence'].next_by_code('supplier.rating') or _('Draft')

        self.state = "confirm"

    def action_approved(self):
        """Approve the record"""
        self.ensure_one()
        self.partner_id.write({
            'next_evaluation_date': self.partner_id.next_evaluation_date + timedelta(days=self.partner_id.evaluation_repeat),
            'pending_evaluation': False
        })
        self.state = "approved"

    def action_rejected(self):
        """Reject the record"""
        self.ensure_one()
        self.state = "reject"

    def action_back_to_draft(self):
        """set to draft the record"""
        self.ensure_one()
        self.state = "draft"

    def action_cancel(self):
        """Cancel the record"""
        self.ensure_one()
        self.state = "cancel"

    @api.depends('line_ids')
    def compute_total(self):
        """Compute total from line"""
        for rec in self:
            total = 0.00
            for lines in rec.line_ids:
                total += lines.score
            rec.total = total

    def action_record_revision(self):
        """Generate Revision No and revision Date for document"""
        self.ensure_one()
        self.revision_no = self.revision_no + 1
        self.revision_date = fields.Date.today()
        self.state = "draft"


class SupplierRatingLine(models.Model):
    _name = 'supplier.rating.line'
    _description = "Supplier rating lines"

    rating_id = fields.Many2one('supplier.rating')
    sequence = fields.Integer(related="category_id.sequence")
    category_id = fields.Many2one('rating.description.category', required=True)
    description_id = fields.Many2one('rating.description', string="Description ID", domain="[('category_id','=', category_id)]")
    description = fields.Text()
    only_category = fields.Boolean(default=False)
    marks = fields.Integer(required=True, default=0)
    category_factor_id = fields.Many2one('rating.description.category.factor', string="Weight Factor", domain="[('category_id','=', category_id)]")
    weight_factor = fields.Integer(required=True, default=0, string="Weight Factor value")
    score = fields.Integer(required=True, default=0, string="Score (Marks x W.F)", store=True, compute="compute_score")

    @api.onchange('description_id')
    def onchange_description_id(self):
        """Get description from when change the description"""
        if self.description_id:
            self.description = self.description_id.description

    @api.onchange('category_factor_id')
    def onchange_category_factor_id(self):
        """Get wight factor from when change the category_factor"""
        if self.category_factor_id:
            self.weight_factor = self.category_factor_id.value

    @api.depends('marks', 'category_factor_id', 'weight_factor')
    def compute_score(self):
        """Compute score value
            Score = Weight factor * marks
        """
        for rec in self:
            if rec.marks and rec.weight_factor:
                rec.score = rec.marks * rec.weight_factor


class RatingDescriptionCategoryFactor(models.Model):
    _name = 'rating.description.category.factor'
    _description = "Supplier rating description Category Factor"

    name = fields.Char("Title", required=True)
    value = fields.Integer("value", required=True, default=0)
    category_id = fields.Many2one('rating.description.category')


class RatingDescriptionCategory(models.Model):
    _name = 'rating.description.category'
    _description = "Supplier rating description Category"

    name = fields.Char("Title", required=True)
    sequence = fields.Integer(default=1, required=True)
    desc_lines = fields.One2many('rating.description.category.factor', 'category_id', string="Evaluations")


class RatingDescription(models.Model):
    _name = 'rating.description'
    _description = "Supplier rating Description"

    name = fields.Char("Title", required=True)
    description = fields.Char("Description", required=True)
    category_id = fields.Many2one('rating.description.category', required=True)

