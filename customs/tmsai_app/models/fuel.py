
from odoo import fields, models


class TmsaiFuelIndex(models.Model):
    _name = 'tmsai.fuel.index'
    _description = 'Fuel Index'
    _order = 'date desc, region'

    region = fields.Char('Region', required=True, index=True)
    date = fields.Date('Date', required=True, index=True)
    index_value = fields.Float('Index Value', digits=(10, 4), required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    notes = fields.Text('Notes')

    _sql_constraints = [
        ('region_date_uniq', 'unique(region, date)', 'The combination of region and date must be unique!'),
    ]


class TmsaiFuelPolicy(models.Model):
    _name = 'tmsai.fuel.policy'
    _description = 'Fuel Policy'
    _order = 'name'

    name = fields.Char('Name', required=True)
    type = fields.Selection([
        ('percent_of_linehaul', 'Percent of Linehaul'),
        ('band_table', 'Band Table'),
    ], 'Policy Type', required=True)

    percent = fields.Float('Percentage', digits=(5, 2),
                          help='Percentage of linehaul cost for fuel surcharge')

    # Band table lines for 'band_table' type
    band_line_ids = fields.One2many('tmsai.fuel.policy.band', 'policy_id', 'Band Lines')

    active = fields.Boolean('Active', default=True)


class TmsaiFuelPolicyBand(models.Model):
    _name = 'tmsai.fuel.policy.band'
    _description = 'Fuel Policy Band'
    _order = 'from_index'

    policy_id = fields.Many2one('tmsai.fuel.policy', 'Policy', required=True, ondelete='cascade')
    from_index = fields.Float('From Index', digits=(10, 4), required=True)
    to_index = fields.Float('To Index', digits=(10, 4), required=True)
    percent = fields.Float('Percentage', digits=(5, 2), required=True)
