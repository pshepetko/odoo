
from odoo import api, fields, models


class TmsaiTrackingEvent(models.Model):
    _name = 'tmsai.tracking.event'
    _description = 'Tracking Event'
    _order = 'timestamp desc'
    _rec_name = 'description'

    document_type = fields.Selection([
        ('TR', 'Transport Request'),
        ('FU', 'Freight Unit'),
        ('FO', 'Freight Order'),
        ('FB', 'Freight Booking'),
    ], 'Document Type', required=True)

    # Technical reference to actual document
    document_id = fields.Integer('Document ID', required=True, index=True,
                                help='Technical reference to the actual document ID')

    event_type = fields.Selection([
        ('pickup', 'Pickup'),
        ('departure', 'Departure'),
        ('checkpoint', 'Checkpoint'),
        ('arrival', 'Arrival'),
        ('pod_received', 'POD Received'),
        ('other', 'Other'),
    ], 'Event Type', required=True)

    timestamp = fields.Datetime('Timestamp', required=True, default=fields.Datetime.now)

    # GPS coordinates
    gps_lat = fields.Float('GPS Latitude', digits=(10, 6))
    gps_lng = fields.Float('GPS Longitude', digits=(10, 6))

    source = fields.Selection([
        ('mobile', 'Mobile App'),
        ('api', 'API'),
        ('manual', 'Manual Entry'),
    ], 'Source', required=True, default='manual')

    description = fields.Text('Description', required=True)
    attachment_ids = fields.Many2many('ir.attachment', 'tmsai_tracking_attachment_rel',
                                      'event_id', 'attachment_id', 'Attachments')

    @api.model
    def create_event(self, document_type, document_id, event_type, description, **kwargs):
        """Helper method to create tracking events"""
        vals = {
            'document_type': document_type,
            'document_id': document_id,
            'event_type': event_type,
            'description': description,
        }
        vals.update(kwargs)
        return self.create(vals)
