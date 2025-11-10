
from odoo import fields, models


class TmsaiGeoZone(models.Model):
    _name = 'tmsai.geo.zone'
    _description = 'Geographic Zone'
    _order = 'name'

    name = fields.Char('Name', required=True)
    type = fields.Selection([
        ('country', 'Country'),
        ('state', 'State/Province'),
        ('city', 'City'),
        ('zip', 'ZIP/Postal Code'),
        ('point', 'Point'),
        ('radius', 'Radius'),
    ], 'Type', required=True, default='country')

    # Location fields
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one('res.country.state', 'State/Province')
    city = fields.Char('City')
    zip = fields.Char('ZIP/Postal Code')

    # Geographic coordinates
    lat = fields.Float('Latitude', digits=(10, 6))
    lng = fields.Float('Longitude', digits=(10, 6))
    radius_km = fields.Float('Radius (km)', digits=(10, 2))

    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name must be unique!'),
    ]
