
from odoo import api, fields, models
from odoo.tools.translate import _


class TmsaiTransportRequest(models.Model):
    _name = 'tmsai.transport.request'
    _description = 'Transport Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    name = fields.Char('Reference', required=True, copy=False, readonly=True,
                      default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('planned', 'Planned'),
        ('in_transit', 'In Transit'),
        ('done', 'Done'),
        ('canceled', 'Canceled'),
    ], 'State', default='draft', tracking=True, index=True)

    # Source information
    transport_category = fields.Selection([
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound'),
        ('internal', 'Internal'),
    ], 'Transport Category', required=True)

    source_model = fields.Selection([
        ('sale.order', 'Sales Order'),
        ('purchase.order', 'Purchase Order'),
        ('stock.picking', 'Stock Picking'),
    ], 'Source Model')

    source_ref = fields.Char('Source Reference')
    source_line_ref = fields.Char('Source Line Reference')
    bill_to_partner_id = fields.Many2one('res.partner', 'Bill To')

    # Parties and locations
    partner_from_id = fields.Many2one('res.partner', 'Shipper', required=True)
    partner_to_id = fields.Many2one('res.partner', 'Consignee', required=True)
    location_from_id = fields.Many2one('stock.location', 'From Location')
    location_to_id = fields.Many2one('stock.location', 'To Location')

    # Route and classification
    lane_from_zone_id = fields.Many2one('tmsai.geo.zone', 'From Zone')
    lane_to_zone_id = fields.Many2one('tmsai.geo.zone', 'To Zone')
    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode', required=True)
    service_level_id = fields.Many2one('tmsai.service.level', 'Service Level')
    requested_unit_id = fields.Many2one('tmsai.unit', 'Requested Unit')
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm')

    # Dates
    planned_pickup = fields.Datetime('Planned Pickup', required=True)
    planned_delivery = fields.Datetime('Planned Delivery', required=True)
    window_pickup_from = fields.Datetime('Pickup Window From')
    window_pickup_to = fields.Datetime('Pickup Window To')
    window_delivery_from = fields.Datetime('Delivery Window From')
    window_delivery_to = fields.Datetime('Delivery Window To')

    # Cargo details
    product_id = fields.Many2one('product.product', 'Product')
    description = fields.Text('Description')
    qty = fields.Float('Quantity', digits=(12, 3))
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    weight = fields.Float('Weight (kg)', digits=(12, 3))
    volume = fields.Float('Volume (m³)', digits=(12, 3))
    packages = fields.Integer('Packages')
    package_type = fields.Char('Package Type')
    is_hazardous = fields.Boolean('Hazardous', default=False)
    temperature_req = fields.Char('Temperature Requirement')

    # Links
    fu_id = fields.Many2one('tmsai.freight.unit', 'Freight Unit', readonly=True)
    split_from_id = fields.Many2one('tmsai.transport.request', 'Split From')

    # Notes
    notes = fields.Text('Notes', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tmsai.tr') or _('New')
        return super().create(vals)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_plan(self):
        self.write({'state': 'planned'})

    def action_in_transit(self):
        self.write({'state': 'in_transit'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'canceled'})
