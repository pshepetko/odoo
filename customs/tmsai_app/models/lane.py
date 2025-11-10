
from odoo import fields, models


class TmsaiLane(models.Model):
    _name = 'tmsai.lane'
    _description = 'Transport Lane'
    _order = 'name'

    name = fields.Char('Name', required=True, index=True)
    from_zone_id = fields.Many2one('tmsai.geo.zone', 'From Zone', required=True)
    to_zone_id = fields.Many2one('tmsai.geo.zone', 'To Zone', required=True)
    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode', required=True)
    default_unit_id = fields.Many2one('tmsai.unit', 'Default Unit')
    sla_lead_time_hours = fields.Float('SLA Lead Time (hours)', digits=(10, 2),
                                     help='Service Level Agreement lead time in hours')
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name must be unique!'),
    ]
