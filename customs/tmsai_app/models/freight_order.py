
from odoo import api, fields, models
from odoo.tools.translate import _


class TmsaiFreightOrder(models.Model):
    _name = 'tmsai.freight.order'
    _description = 'Freight Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    name = fields.Char('Reference', required=True, copy=False, readonly=True,
                      default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('tendering', 'Tendering'),
        ('confirmed', 'Confirmed'),
        ('dispatched', 'Dispatched'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('closed', 'Closed'),
        ('canceled', 'Canceled'),
    ], 'State', default='draft', tracking=True, index=True)

    # Execution details
    execution_mode = fields.Selection([
        ('own_fleet', 'Own Fleet'),
        ('subcontracted', 'Subcontracted'),
    ], 'Execution Mode', required=True)

    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode', required=True)
    service_level_id = fields.Many2one('tmsai.service.level', 'Service Level')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)

    # Schedule
    planned_departure = fields.Datetime('Planned Departure', required=True)
    planned_arrival = fields.Datetime('Planned Arrival', required=True)
    lane_id = fields.Many2one('tmsai.lane', 'Lane')

    # Carrier
    carrier_id = fields.Many2one('tmsai.carrier', 'Carrier')
    carrier_partner_id = fields.Char('Carrier Name', related='carrier_id.partner_id.name', store=True)

    # Cargo
    fu_ids = fields.Many2many('tmsai.freight.unit', string='Freight Units')

    # Resources
    resource_line_ids = fields.One2many('tmsai.fo.resource', 'fo_id', 'Resource Lines')

    # Computed capacity totals
    capacity_weight = fields.Float('Capacity Weight (kg)', digits=(12, 3),
                                  compute='_compute_capacity_totals', store=True)
    capacity_volume = fields.Float('Capacity Volume (m³)', digits=(12, 3),
                                  compute='_compute_capacity_totals', store=True)
    capacity_pallets = fields.Integer('Capacity Pallets',
                                    compute='_compute_capacity_totals', store=True)

    # Route
    route_leg_ids = fields.One2many('tmsai.route.leg', 'fo_id', 'Route Legs')

    # Financials
    cost_line_ids = fields.One2many('tmsai.cost.line', 'fo_id', 'Cost Lines')
    revenue_line_ids = fields.One2many('tmsai.revenue.line', 'fo_id', 'Revenue Lines')

    totals_cost = fields.Float('Total Cost', digits=(12, 2),
                               compute='_compute_financial_totals', store=True)
    totals_revenue = fields.Float('Total Revenue', digits=(12, 2),
                                 compute='_compute_financial_totals', store=True)
    margin = fields.Float('Margin', digits=(12, 2),
                         compute='_compute_financial_totals', store=True)

    # Notes
    notes = fields.Text('Notes', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tmsai.fo') or _('New')
        return super().create(vals)

    @api.depends('resource_line_ids.capacity_weight', 'resource_line_ids.capacity_volume',
                 'resource_line_ids.capacity_pallets')
    def _compute_capacity_totals(self):
        for fo in self:
            total_weight = sum(line.capacity_weight for line in fo.resource_line_ids if line.capacity_weight)
            total_volume = sum(line.capacity_volume for line in fo.resource_line_ids if line.capacity_volume)
            total_pallets = sum(line.capacity_pallets for line in fo.resource_line_ids if line.capacity_pallets)

            fo.capacity_weight = total_weight
            fo.capacity_volume = total_volume
            fo.capacity_pallets = total_pallets

    @api.depends('cost_line_ids.amount_total', 'revenue_line_ids.amount_total')
    def _compute_financial_totals(self):
        for fo in self:
            total_cost = sum(line.amount_total for line in fo.cost_line_ids if line.amount_total)
            total_revenue = sum(line.amount_total for line in fo.revenue_line_ids if line.amount_total)

            fo.totals_cost = total_cost
            fo.totals_revenue = total_revenue
            fo.margin = total_revenue - total_cost

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_dispatch(self):
        self.write({'state': 'dispatched'})

    def action_in_transit(self):
        self.write({'state': 'in_transit'})

    def action_delivered(self):
        self.write({'state': 'delivered'})

    def action_close(self):
        self.write({'state': 'closed'})

    def action_cancel(self):
        self.write({'state': 'canceled'})


class TmsaiFoResource(models.Model):
    _name = 'tmsai.fo.resource'
    _description = 'FO Resource Line'
    _order = 'fo_id, sequence'

    fo_id = fields.Many2one('tmsai.freight.order', 'Freight Order', required=True, ondelete='cascade')
    resource_id = fields.Many2one('tmsai.resource', 'Resource', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    driver_id = fields.Many2one('res.partner', 'Driver')

    role = fields.Selection([
        ('tractor', 'Tractor'),
        ('trailer', 'Trailer'),
        ('wagon', 'Wagon'),
        ('other', 'Other'),
    ], 'Role', required=True)

    unit_line_ids = fields.One2many('tmsai.fo.resource.unit', 'fo_resource_id', 'Unit Lines')

    # Computed capacities
    capacity_weight = fields.Float('Capacity Weight (kg)', digits=(12, 3),
                                  compute='_compute_capacities', store=True)
    capacity_volume = fields.Float('Capacity Volume (m³)', digits=(12, 3),
                                  compute='_compute_capacities', store=True)
    capacity_pallets = fields.Integer('Capacity Pallets',
                                    compute='_compute_capacities', store=True)

    # Availability
    planned_from = fields.Datetime('Planned From')
    planned_to = fields.Datetime('Planned To')
    state = fields.Selection([
        ('planned', 'Planned'),
        ('assigned', 'Assigned'),
        ('in_use', 'In Use'),
        ('released', 'Released'),
    ], 'State', default='planned')

    sequence = fields.Integer('Sequence', default=10)

    @api.depends('unit_line_ids.quantity', 'unit_line_ids.unit_id.capacity_weight',
                 'unit_line_ids.unit_id.capacity_volume', 'unit_line_ids.unit_id.pallets')
    def _compute_capacities(self):
        for resource_line in self:
            total_weight = 0
            total_volume = 0
            total_pallets = 0

            for line in resource_line.unit_line_ids:
                qty = line.quantity or 1
                total_weight += line.unit_id.capacity_weight * qty
                total_volume += line.unit_id.capacity_volume * qty
                total_pallets += line.unit_id.pallets * qty

            resource_line.capacity_weight = total_weight
            resource_line.capacity_volume = total_volume
            resource_line.capacity_pallets = total_pallets


class TmsaiFoResourceUnit(models.Model):
    _name = 'tmsai.fo.resource.unit'
    _description = 'FO Resource Unit'
    _order = 'fo_resource_id, sequence'

    fo_resource_id = fields.Many2one('tmsai.fo.resource', 'FO Resource', required=True, ondelete='cascade')
    unit_id = fields.Many2one('tmsai.unit', 'Unit', required=True)
    quantity = fields.Integer('Quantity', default=1, required=True)
    sequence = fields.Integer('Sequence', default=10)
