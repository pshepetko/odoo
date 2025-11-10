
from odoo import api, fields, models
from odoo.tools.translate import _


class TmsaiFreightUnit(models.Model):
    _name = 'tmsai.freight.unit'
    _description = 'Freight Unit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    name = fields.Char('Reference', required=True, copy=False, readonly=True,
                      default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                default=lambda self: self.env.company)

    # Transport Requests
    tr_ids = fields.One2many('tmsai.transport.request', 'fu_id', 'Transport Requests')

    # Classification
    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode', required=True)
    planned_unit_id = fields.Many2one('tmsai.unit', 'Planned Unit')

    # Computed totals
    weight_total = fields.Float('Total Weight (kg)', digits=(12, 3),
                               compute='_compute_totals', store=True)
    volume_total = fields.Float('Total Volume (m³)', digits=(12, 3),
                               compute='_compute_totals', store=True)
    packages = fields.Integer('Total Packages',
                             compute='_compute_totals', store=True)

    # Consolidation key
    consolidation_key = fields.Char('Consolidation Key',
                                   compute='_compute_consolidation_key', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('assigned', 'Assigned'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ], 'State', default='draft', tracking=True, index=True)

    notes = fields.Text('Notes', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tmsai.fu') or _('New')
        return super().create(vals)

    @api.depends('tr_ids.weight', 'tr_ids.volume', 'tr_ids.packages')
    def _compute_totals(self):
        for fu in self:
            total_weight = sum(tr.weight for tr in fu.tr_ids if tr.weight)
            total_volume = sum(tr.volume for tr in fu.tr_ids if tr.volume)
            total_packages = sum(tr.packages for tr in fu.tr_ids if tr.packages)

            fu.weight_total = total_weight
            fu.volume_total = total_volume
            fu.packages = total_packages

    @api.depends('mode_id', 'planned_unit_id', 'tr_ids.lane_from_zone_id',
                 'tr_ids.lane_to_zone_id', 'tr_ids.service_level_id',
                 'tr_ids.planned_pickup', 'tr_ids.is_hazardous')
    def _compute_consolidation_key(self):
        for fu in self:
            if not fu.tr_ids:
                fu.consolidation_key = ''
                continue

            # Get first TR for reference
            first_tr = fu.tr_ids[0]

            # Build consolidation key based on grouping criteria
            key_parts = [
                str(fu.mode_id.id or ''),
                str(first_tr.lane_from_zone_id.id or ''),
                str(first_tr.lane_to_zone_id.id or ''),
                str(first_tr.service_level_id.id or ''),
                str(fu.planned_unit_id.id or ''),
                first_tr.planned_pickup.strftime('%Y-%m-%d') if first_tr.planned_pickup else '',
                '1' if first_tr.is_hazardous else '0',
            ]

            fu.consolidation_key = '|'.join(key_parts)

    def action_plan(self):
        self.write({'state': 'planned'})

    def action_assign(self):
        self.write({'state': 'assigned'})

    def action_in_transit(self):
        self.write({'state': 'in_transit'})

    def action_delivered(self):
        self.write({'state': 'delivered'})

    def action_cancel(self):
        self.write({'state': 'canceled'})
