# TMS AI - Transportation Management System

A comprehensive Transportation Management System for Odoo 19 with AI capabilities.

## Features

### Core Operations
- **Transport Request Management**: Unified OTR/DTR system with linear structure
- **Freight Unit Consolidation**: Automatic grouping and bin packing algorithms
- **Freight Order Management**: Complete dispatch and execution workflow
- **Freight Booking**: Subcontractor booking and tendering system
- **Freight Settlement**: Automated billing and settlement processing

### Master Data Management
- **Carrier Management**: Complete carrier profiles with documents and lane coverage
- **Resource Management**: Fleet and resource composition tracking
- **Unit Management**: Container, trailer, and other transport unit catalog
- **Geo Zones**: Geographic zoning and lane management
- **Service Levels**: Service level agreements and KPI tracking
- **Rate Management**: Complex rating engine with multiple pricing methods
- **Fuel Management**: Fuel index tracking and surcharge policies

### Advanced Features
- **Tendering System**: Automated carrier tendering and quote comparison
- **Tracking & Visibility**: Real-time tracking with GPS integration
- **Multi-Company Support**: Full multi-company capabilities
- **Integration**: Seamless integration with Sales, Purchase, Stock, and Accounting

## Installation

1. Copy the `tmsai_app` folder to your Odoo addons directory
2. Update your addons list: `./odoo-bin -u base --stop-after-init`
3. Install the module from Apps menu or via command line: `./odoo-bin -i tmsai_app`

## Dependencies

This module requires the following Odoo modules:
- base
- mail
- sale
- purchase
- stock
- account
- uom
- fleet
- contacts
- web
- calendar
- base_geolocalize
- delivery

## Configuration

After installation, configure the module through:
- Settings → TMS → Configuration
- Set up master data (Carriers, Units, Resources, Geo Zones, etc.)
- Configure service levels and agreements
- Set up fuel policies and indices

## Security Groups

The module provides five security groups:
- **TMS User**: Basic operational access
- **TMS Planner**: Full planning and dispatch capabilities
- **TMS Billing**: Settlement and billing access
- **TMS Master Data Manager**: Configuration and master data management
- **TMS Manager**: Full system access

## Support

For support and documentation, visit: https://tms-ai.com/support

## License

This module is licensed under LGPL-3.