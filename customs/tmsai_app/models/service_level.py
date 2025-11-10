
from odoo import fields, models


class TmsaiServiceLevel(models.Model):
    _name = 'tmsai.service.level'
    _description = 'Service Level'
    _order = 'code'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', required=True, index=True)
    description = fields.Text('Description', translate=True)
    kpi_ontime_pct = fields.Float('KPI On-Time %', digits=(5, 2), help='Target on-time delivery percentage')
    kpi_lead_time_hours = fields.Float('KPI Lead Time (hours)', digits=(10, 2), help='Standard lead time in hours')
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The code must be unique!'),
    ]
