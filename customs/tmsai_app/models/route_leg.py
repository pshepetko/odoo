
from odoo import fields, models


class TmsaiRouteLeg(models.Model):
    _name = 'tmsai.route.leg'
    _description = 'Route Leg'
    _order = 'fo_id, sequence'

    fo_id = fields.Many2one('tmsai.freight.order', 'Freight Order', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)

    # Locations
    from_partner_id = fields.Many2one('res.partner', 'From Partner', required=True)
    to_partner_id = fields.Many2one('res.partner', 'To Partner', required=True)
    from_location_id = fields.Many2one('stock.location', 'From Location')
    to_location_id = fields.Many2one('stock.location', 'To Location')

    # Schedule
    planned_departure = fields.Datetime('Planned Departure')
    planned_arrival = fields.Datetime('Planned Arrival')

    # Distance and duration
    distance_km = fields.Float('Distance (km)', digits=(10, 2))
    duration_min = fields.Float('Duration (minutes)', digits=(8, 2))

    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode')
    carrier_id = fields.Many2one('tmsai.carrier', 'Carrier')

    notes = fields.Text('Notes')
