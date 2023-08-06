from odoo import fields, models, api, _

class SubscriptionRequest(models.Model):

    _inherit = ["subscription.request"]

    gender = fields.Selection(
        [
            ("male", _("Male")),
            ("female", _("Female")),
            ("other", _("Other")),
            ("no_answer", _("No answer"))
        ],
        string="Gender",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    discovery_channel = fields.Selection(
        [
            ('recommendation', _('Recommendation')),
            ('newsletter', _('Newsletter')),
            ('social_network', _('Social network')),
            ('press', _('Press')),
            ('advertisement', _('Advertisement')),
            ('federation', _('Federation or organization')),
            ('others', _('Others'))
        ],
        help = 'How people find us.',
        string = _('How did you know about us?'),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    newsletter_approved = fields.Boolean(
        string='Newsletter approved',
        default=False,
    )
    sepa_approved = fields.Boolean(
        string = _('SEPA authorization'),
        required=True,
        default=False,
    )
    ref = fields.Char(string='Internal Reference', index=True)

    def get_partner_vals(self):
        partner_vals = super().get_partner_vals()
        partner_vals['ref'] = self.ref
        return partner_vals

    def get_invoice_vals(self, partner):
        vals = super().get_invoice_vals(partner)
        usense = self.env['operating.unit'].search([('code','=','USense')])
        vals['operating_unit_id'] = usense.id
        return vals

    @api.multi
    def validate_subscription_request(self):
        invoice = super().validate_subscription_request()
        if self.ref:
            self.partner_id.ref = self.ref
        return invoice
