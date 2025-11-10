
from odoo import api, fields, models


class TmsaiUnit(models.Model):
    _name = 'tmsai.unit'
    _description = 'Transport Unit'
    _order = 'code'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True, index=True,
                      help='Unit code like 20GP, 40HC, 13.6m Trailer, etc.')
    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode', required=True)

    category = fields.Selection([
        ('container', 'Container'),
        ('trailer', 'Trailer'),
        ('semi_trailer', 'Semi-Trailer'),
        ('wagon', 'Rail Wagon'),
        ('uld', 'Unit Load Device'),
        ('body', 'Truck Body'),
        ('tank', 'Tank'),
        ('platform', 'Platform'),
        ('other', 'Other'),
    ], 'Category', required=True)

    # Physical characteristics
    size_label = fields.Char('Size Label', help='Display size like "20ft", "40ft HC", etc.')
    tare_weight = fields.Float('Tare Weight (kg)', digits=(10, 3),
                              help='Empty weight of the unit')
    capacity_weight = fields.Float('Capacity Weight (kg)', digits=(10, 3))
    capacity_volume = fields.Float('Capacity Volume (m³)', digits=(10, 3))
    pallets = fields.Integer('Pallet Spaces')

    # Dimensions
    length = fields.Float('Length (m)', digits=(8, 3))
    width = fields.Float('Width (m)', digits=(8, 3))
    height = fields.Float('Height (m)', digits=(8, 3))

    # Special requirements
    is_reefer = fields.Boolean('Reefer/Refrigerated', default=False)
    is_hazmat = fields.Boolean('Hazardous Materials', default=False)
    door_type = fields.Selection([
        ('standard', 'Standard'),
        ('roll_up', 'Roll-up'),
        ('barn', 'Barn'),
        ('curtain', 'Curtain'),
        ('other', 'Other'),
    ], 'Door Type')

    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The code must be unique!'),
    ]


class TmsaiResource(models.Model):
    _name = 'tmsai.resource'
    _description = 'Transport Resource'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Name', required=True, index=True)
    code = fields.Char('Code', required=True, index=True)
    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode', required=True)

    category = fields.Selection([
        ('tractor', 'Tractor'),
        ('truck', 'Truck'),
        ('trailer_set', 'Trailer Set'),
        ('train', 'Train'),
        ('wagon_set', 'Wagon Set'),
        ('chassis', 'Chassis'),
        ('container_set', 'Container Set'),
        ('other', 'Other'),
    ], 'Category', required=True)

    owner_type = fields.Selection([
        ('company', 'Company'),
        ('carrier', 'Carrier'),
    ], 'Owner Type', required=True, default='company')

    carrier_id = fields.Many2one('tmsai.carrier', 'Carrier')
    partner_owner_id = fields.Many2one('res.partner', 'Owner Partner', related='carrier_id.partner_id', store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

    # Composition
    unit_line_ids = fields.One2many('tmsai.resource.unit', 'resource_id', 'Unit Lines')

    # Computed capacities
    total_capacity_weight = fields.Float('Total Capacity Weight (kg)', digits=(10, 3),
                                        compute='_compute_capacities', store=True)
    total_capacity_volume = fields.Float('Total Capacity Volume (m³)', digits=(10, 3),
                                        compute='_compute_capacities', store=True)
    total_pallets = fields.Integer('Total Pallet Spaces',
                                  compute='_compute_capacities', store=True)

    active = fields.Boolean('Active', default=True, tracking=True)

    @api.depends('unit_line_ids.quantity', 'unit_line_ids.unit_id.capacity_weight',
                 'unit_line_ids.unit_id.capacity_volume', 'unit_line_ids.unit_id.pallets')
    def _compute_capacities(self):
        for resource in self:
            total_weight = 0
            total_volume = 0
            total_pallets = 0

            for line in resource.unit_line_ids:
                qty = line.quantity or 1
                total_weight += line.unit_id.capacity_weight * qty
                total_volume += line.unit_id.capacity_volume * qty
                total_pallets += line.unit_id.pallets * qty

            resource.total_capacity_weight = total_weight
            resource.total_capacity_volume = total_volume
            resource.total_pallets = total_pallets

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The code must be unique!'),
    ]


class TmsaiResourceUnit(models.Model):
    _name = 'tmsai.resource.unit'
    _description = 'Resource Unit Composition'
    _order = 'resource_id, sequence'

    resource_id = fields.Many2one('tmsai.resource', 'Resource', required=True, ondelete='cascade')
    unit_id = fields.Many2one('tmsai.unit', 'Unit', required=True)
    quantity = fields.Integer('Quantity', default=1, required=True)
    sequence = fields.Integer('Sequence', default=10)
    notes = fields.Char('Notes')
