
from odoo import api, fields, models


class TmsaiCarrier(models.Model):
    _name = 'tmsai.carrier'
    _description = 'Carrier'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Name', required=True, index=True)
    code = fields.Char('Code', required=True, index=True)
    partner_id = fields.Many2one('res.partner', 'Related Partner', required=True,
                                help='Link to the partner record')
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                default=lambda self: self.env.company)
    carrier_type = fields.Selection([
        ('own_fleet', 'Own Fleet'),
        ('subcontractor', 'Subcontractor'),
        ('both', 'Both'),
    ], 'Carrier Type', required=True, default='subcontractor')

    mode_ids = fields.Many2many('tmsai.mode', 'tmsai_carrier_mode_rel',
                                'carrier_id', 'mode_id', 'Transport Modes')
    service_level_ids = fields.Many2many('tmsai.service.level', 'tmsai_carrier_service_rel',
                                         'carrier_id', 'service_level_id', 'Service Levels')

    rating = fields.Float('Rating', digits=(3, 2), help='Carrier performance rating (1-5)')
    blacklisted = fields.Boolean('Blacklisted', default=False)
    notes = fields.Text('Notes')
    active = fields.Boolean('Active', default=True, tracking=True)

    # Related fields
    carrier_partner_id = fields.Char('Partner Name', related='partner_id.name', store=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The code must be unique!'),
    ]


class TmsaiCarrierDocument(models.Model):
    _name = 'tmsai.carrier.document'
    _description = 'Carrier Document'
    _order = 'date_expiry desc'

    carrier_id = fields.Many2one('tmsai.carrier', 'Carrier', required=True, ondelete='cascade')
    doc_type = fields.Selection([
        ('insurance', 'Insurance'),
        ('license', 'License'),
        ('permit', 'Permit'),
        ('contract', 'Contract'),
        ('other', 'Other'),
    ], 'Document Type', required=True)
    number = fields.Char('Document Number', required=True)
    date_issue = fields.Date('Issue Date')
    date_expiry = fields.Date('Expiry Date')
    attachment_id = fields.Many2one('ir.attachment', 'Attachment')
    state = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
    ], 'State', compute='_compute_state', store=True)
    notes = fields.Text('Notes')

    @api.depends('date_expiry')
    def _compute_state(self):
        today = fields.Date.today()
        for doc in self:
            if not doc.date_expiry:
                doc.state = 'valid'
            else:
                days_to_expiry = (doc.date_expiry - today).days
                if days_to_expiry < 0:
                    doc.state = 'expired'
                elif days_to_expiry <= 30:
                    doc.state = 'expiring'
                else:
                    doc.state = 'valid'


class TmsaiCarrierLane(models.Model):
    _name = 'tmsai.carrier.lane'
    _description = 'Carrier Lane Coverage'
    _order = 'carrier_id, from_zone_id, to_zone_id'

    carrier_id = fields.Many2one('tmsai.carrier', 'Carrier', required=True, ondelete='cascade')
    from_zone_id = fields.Many2one('tmsai.geo.zone', 'From Zone', required=True)
    to_zone_id = fields.Many2one('tmsai.geo.zone', 'To Zone', required=True)
    mode_id = fields.Many2one('tmsai.mode', 'Transport Mode', required=True)
    unit_id = fields.Many2one('tmsai.unit', 'Unit')
    lead_time_days = fields.Float('Lead Time (days)', digits=(10, 2))

    # Capacity constraints
    min_weight = fields.Float('Min Weight (kg)', digits=(10, 3))
    max_weight = fields.Float('Max Weight (kg)', digits=(10, 3))
    min_volume = fields.Float('Min Volume (m³)', digits=(10, 3))
    max_volume = fields.Float('Max Volume (m³)', digits=(10, 3))

    active = fields.Boolean('Active', default=True)
