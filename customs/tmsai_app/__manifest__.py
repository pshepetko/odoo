{
    'name': 'TMS AI - Transportation Management System',
    'version': '19.0.1.0.0',
    'category': 'Transportation',
    'summary': 'Advanced Transportation Management System with AI capabilities',
    'description': """
        TMS AI - Comprehensive Transportation Management System

        Features:
        * Transport Request Management (OTR/DTR unified)
        * Freight Unit Consolidation
        * Freight Order and Booking Management
        * Carrier and Resource Management
        * Rate Management and Tendering
        * Freight Settlement and Billing
        * Tracking and Visibility
        * Master Data Management (Carriers, Units, Resources, Geo Zones, Lanes, etc.)
        * Multi-company support
        * Advanced routing and scheduling
        * Cost and revenue tracking
        * Integration with Sales, Purchase, Stock, and Accounting modules
    """,
    'author': 'TMS AI Team',
    'website': 'https://tms-ai.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'sale',
        'purchase',
        'stock',
        'account',
        'uom',
        'fleet',
        'contacts',
        'web',
        'calendar',
        'base_geolocalize',
        'delivery',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',

        # Data
        'data/tmsai_data.xml',
        'data/ir_sequence.xml',

        # Views
        'views/tmsai_menu.xml',
        'views/mode_views.xml',
        'views/service_level_views.xml',
        'views/geo_zone_views.xml',
        'views/lane_views.xml',
        'views/carrier_views.xml',
        'views/unit_views.xml',
        'views/resource_views.xml',
        'views/freight_agreement_views.xml',
        'views/accessorial_views.xml',
        'views/fuel_views.xml',
        'views/transport_request_views.xml',
        'views/freight_unit_views.xml',
        'views/freight_order_views.xml',
        'views/freight_booking_views.xml',
        'views/route_leg_views.xml',
        'views/tender_views.xml',
        'views/freight_settlement_views.xml',
        'views/cost_revenue_views.xml',
        'views/tracking_views.xml',

        # Reports
        'reports/tmsai_reports.xml',

        # Configuration
        'data/res_config_settings_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [
        'demo/tmsai_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 100,
    'images': ['static/description/banner.png'],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
}
