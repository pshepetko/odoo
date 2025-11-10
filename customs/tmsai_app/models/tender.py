
from odoo import fields, models


class TmsaiTender(models.Model):
    _name = 'tmsai.tender'
    _description = 'Freight Tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    name = fields.Char('Reference', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                default=lambda self: self.env.company)

    # Links to FO or FB
    fo_id = fields.Many2one('tmsai.freight.order', 'Freight Order')
    fb_id = fields.Many2one('tmsai.freight.booking', 'Freight Booking')

    # Tender details
    invited_carrier_ids = fields.Many2many('tmsai.carrier', 'tmsai_tender_carrier_rel',
                                           'tender_id', 'carrier_id', 'Invited Carriers')
    awarding_rule = fields.Selection([
        ('lowest_cost', 'Lowest Cost'),
        ('best_eta', 'Best ETA'),
        ('scorecard', 'Scorecard'),
        ('manual', 'Manual'),
    ], 'Awarding Rule', required=True, default='lowest_cost')

    deadline = fields.Datetime('Deadline', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('quoted', 'Quoted'),
        ('awarded', 'Awarded'),
        ('lost', 'Lost'),
        ('canceled', 'Canceled'),
    ], 'State', default='draft', tracking=True, index=True)

    # Quotes
    quote_line_ids = fields.One2many('tmsai.tender.quote', 'tender_id', 'Quotes')
    awarded_carrier_id = fields.Many2one('tmsai.carrier', 'Awarded Carrier')

    notes = fields.Text('Notes', tracking=True)

    def action_send(self):
        self.write({'state': 'sent'})

    def action_award(self):
        # Find best quote based on awarding rule and award it
        if self.awarding_rule == 'lowest_cost':
            best_quote = min(self.quote_line_ids.filtered(lambda q: q.selected),
                           key=lambda q: q.price_linehaul)
        elif self.awarding_rule == 'best_eta':
            best_quote = min(self.quote_line_ids.filtered(lambda q: q.selected),
                           key=lambda q: q.eta_hours)
        else:
            # Manual or scorecard - need manual selection
            return

        if best_quote:
            self.write({
                'state': 'awarded',
                'awarded_carrier_id': best_quote.carrier_id.id,
            })

    def action_cancel(self):
        self.write({'state': 'canceled'})


class TmsaiTenderQuote(models.Model):
    _name = 'tmsai.tender.quote'
    _description = 'Tender Quote'
    _order = 'tender_id, carrier_id'

    tender_id = fields.Many2one('tmsai.tender', 'Tender', required=True, ondelete='cascade')
    carrier_id = fields.Many2one('tmsai.carrier', 'Carrier', required=True)

    # Pricing
    price_linehaul = fields.Float('Linehaul Price', digits=(12, 2), required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    accessorial_total = fields.Float('Accessorial Total', digits=(12, 2))
    fuel_percent = fields.Float('Fuel Surcharge %', digits=(5, 2))

    # Delivery
    eta_hours = fields.Float('ETA (hours)', digits=(8, 2))
    valid_until = fields.Datetime('Valid Until')

    # Selection
    selected = fields.Boolean('Selected', default=False)

    # Attachments and notes
    attachment_ids = fields.Many2many('ir.attachment', 'tmsai_tender_quote_attachment_rel',
                                      'quote_id', 'attachment_id', 'Attachments')
    notes = fields.Text('Notes')
