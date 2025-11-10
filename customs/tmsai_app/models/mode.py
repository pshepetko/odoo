
from odoo import fields, models


class TmsaiMode(models.Model):
    _name = 'tmsai.mode'
    _description = 'Transport Mode'
    _order = 'code'

    code = fields.Char('Code', required=True, index=True)
    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The code must be unique!'),
    ]
