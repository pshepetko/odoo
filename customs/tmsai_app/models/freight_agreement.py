
from odoo import api, fields, models
from odoo.tools.translate import _


class TmsaiFreightAgreement(models.Model):
    _name = 'tmsai.freight.agreement'
    _description = 'Freight Agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Name', required=True, index=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                default=lambda self: self.env.company)

    role = fields.Selection([
        ('carrier_cost', 'Carrier Cost'),
        ('customer_price', 'Customer Price'),
    ], 'Agreement Role', required=True)

    carrier_id = fields.Many2one('tmsai.carrier', 'Carrier')
    customer_id = fields.Many2one('res.partner', 'Customer')

    date_from = fields.Date('Valid From', required=True)
    date_to = fields.Date('Valid To', required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)

    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode')
    service_level_id = fields.Many2one('tmsai.service.level', 'Service Level')
    default_unit_id = fields.Many2one('tmsai.unit', 'Default Unit')
    fuel_policy_id = fields.Many2one('tmsai.fuel.policy', 'Fuel Policy')

    terms_text = fields.Html('Terms and Conditions')
    active = fields.Boolean('Active', default=True, tracking=True)

    # Rate lines
    rate_line_ids = fields.One2many('tmsai.freight.rate', 'agreement_id', 'Rate Lines')

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for agreement in self:
            if agreement.date_from and agreement.date_to:
                if agreement.date_from > agreement.date_to:
                    error_msg = _('Valid From date must be before Valid To date.')
                    raise models.ValidationError(error_msg)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name must be unique!'),
    ]


class TmsaiFreightRate(models.Model):
    _name = 'tmsai.freight.rate'
    _description = 'Freight Rate'
    _order = 'priority desc, agreement_id, lane_id'

    agreement_id = fields.Many2one('tmsai.freight.agreement', 'Agreement', required=True, ondelete='cascade')

    # Route definition (either lane or from/to zones)
    lane_id = fields.Many2one('tmsai.lane', 'Lane')
    from_zone_id = fields.Many2one('tmsai.geo.zone', 'From Zone')
    to_zone_id = fields.Many2one('tmsai.geo.zone', 'To Zone')

    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode')
    unit_id = fields.Many2one('tmsai.unit', 'Unit')

    # Pricing method
    price_method = fields.Selection([
        ('flat', 'Flat Rate'),
        ('per_km', 'Per Kilometer'),
        ('per_kg', 'Per Kilogram'),
        ('per_m3', 'Per Cubic Meter'),
        ('per_pallet', 'Per Pallet'),
        ('tiered', 'Tiered Pricing'),
    ], 'Price Method', required=True, default='flat')

    base_price = fields.Float('Base Price', digits=(10, 2), required=True)
    volumetric_factor = fields.Float('Volumetric Factor', digits=(6, 3),
                                    help='Factor to calculate chargeable weight from volume')
    min_charge = fields.Float('Minimum Charge', digits=(10, 2))

    # Capacity constraints
    min_weight = fields.Float('Min Weight (kg)', digits=(10, 3))
    max_weight = fields.Float('Max Weight (kg)', digits=(10, 3))
    min_volume = fields.Float('Min Volume (m³)', digits=(10, 3))
    max_volume = fields.Float('Max Volume (m³)', digits=(10, 3))
    min_pallets = fields.Integer('Min Pallets')
    max_pallets = fields.Integer('Max Pallets')

    lead_time_days = fields.Float('Lead Time (days)', digits=(10, 2))
    taxes_id = fields.Many2many('account.tax', string='Taxes')
    priority = fields.Integer('Priority', default=10,
                            help='Higher priority rates are selected first')
    active = fields.Boolean('Active', default=True)
