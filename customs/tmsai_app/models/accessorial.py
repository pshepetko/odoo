
from odoo import fields, models


class TmsaiAccessorial(models.Model):
    _name = 'tmsai.accessorial'
    _description = 'Accessorial Charge'
    _order = 'code'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', required=True, index=True)
    product_id = fields.Many2one('product.product', 'Related Product', required=True)

    charge_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('per_hour', 'Per Hour'),
        ('per_km', 'Per Kilometer'),
        ('per_stop', 'Per Stop'),
        ('per_package', 'Per Package'),
        ('waiting_time', 'Waiting Time'),
        ('detention', 'Detention'),
        ('customs', 'Customs'),
        ('liftgate', 'Liftgate'),
        ('toll', 'Toll'),
        ('other', 'Other'),
    ], 'Charge Type', required=True)

    price = fields.Float('Price', digits=(10, 2), required=True)
    min_charge = fields.Float('Minimum Charge', digits=(10, 2))
    free_time_min = fields.Integer('Free Time (minutes)',
                                  help='Free time before charges apply')
    conditions_json = fields.Text('Conditions',
                                 help='JSON format conditions for applying this charge')
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The code must be unique!'),
    ]
