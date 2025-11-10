
from odoo import api, fields, models
from odoo.tools.translate import _


class TmsaiFreightBooking(models.Model):
    _name = 'tmsai.freight.booking'
    _description = 'Freight Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    name = fields.Char('Reference', required=True, copy=False, readonly=True,
                      default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('quoted', 'Quoted'),
        ('confirmed', 'Confirmed'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('closed', 'Closed'),
        ('canceled', 'Canceled'),
    ], 'State', default='draft', tracking=True, index=True)

    # Details
    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode', required=True)
    service_level_id = fields.Many2one('tmsai.service.level', 'Service Level')
    carrier_id = fields.Many2one('tmsai.carrier', 'Carrier')
    lane_id = fields.Many2one('tmsai.lane', 'Lane')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)

    # Schedule windows
    departure_window_from = fields.Datetime('Departure Window From')
    departure_window_to = fields.Datetime('Departure Window To')
    arrival_window_from = fields.Datetime('Arrival Window From')
    arrival_window_to = fields.Datetime('Arrival Window To')

    # Cargo
    fu_ids = fields.Many2many('tmsai.freight.unit', string='Freight Units')
    resource_hint_unit_id = fields.Many2one('tmsai.unit', 'Resource Hint Unit')

    # Financials
    cost_line_ids = fields.One2many('tmsai.cost.line', 'fb_id', 'Cost Lines')
    revenue_line_ids = fields.One2many('tmsai.revenue.line', 'fb_id', 'Revenue Lines')

    # Tender reference
    tender_id = fields.Many2one('tmsai.tender', 'Tender')

    # Notes
    notes = fields.Text('Notes', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tmsai.fb') or _('New')
        return super().create(vals)

    def action_request_quote(self):
        # Create tender from booking
        self.write({'state': 'quoted'})

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_in_transit(self):
        self.write({'state': 'in_transit'})

    def action_delivered(self):
        self.write({'state': 'delivered'})

    def action_close(self):
        self.write({'state': 'closed'})

    def action_cancel(self):
        self.write({'state': 'canceled'})
