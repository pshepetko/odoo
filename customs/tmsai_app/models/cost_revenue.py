

from odoo import api, fields, models


class TmsaiCostLine(models.Model):
    _name = 'tmsai.cost.line'
    _description = 'Cost Line'
    _order = 'name'

    name = fields.Char('Description', required=True)

    # Links to parent documents
    fsd_id = fields.Many2one('tmsai.freight.settlement', 'Settlement', ondelete='cascade')
    fo_id = fields.Many2one('tmsai.freight.order', 'Freight Order', ondelete='cascade')
    fb_id = fields.Many2one('tmsai.freight.booking', 'Freight Booking', ondelete='cascade')

    # Product and pricing
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float('Quantity', digits=(12, 3), required=True, default=1.0)
    price_unit = fields.Float('Unit Price', digits=(12, 2), required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    taxes_id = fields.Many2many('account.tax', string='Taxes')

    # Computed amounts
    amount_subtotal = fields.Float('Subtotal', digits=(12, 2),
                                  compute='_compute_amounts', store=True)
    amount_total = fields.Float('Total', digits=(12, 2),
                               compute='_compute_amounts', store=True)

    # Rate and agreement references
    agreement_id = fields.Many2one('tmsai.freight.agreement', 'Agreement')
    rate_id = fields.Many2one('tmsai.freight.rate', 'Rate')
    accessorial_id = fields.Many2one('tmsai.accessorial', 'Accessorial')
    is_fuel_surcharge = fields.Boolean('Is Fuel Surcharge', default=False)

    # Calculation details
    calc_json = fields.Text('Calculation Details', readonly=True)

    # Cost accounting
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    cost_center_id = fields.Many2one('account.analytic.account', 'Cost Center')

    @api.depends('quantity', 'price_unit', 'taxes_id')
    def _compute_amounts(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            line.amount_subtotal = subtotal

            # Calculate tax amount
            taxes = line.taxes_id.compute_all(line.price_unit, line.currency_id,
                                             line.quantity, product=line.product_id)
            line.amount_total = taxes['total_included']


class TmsaiRevenueLine(models.Model):
    _name = 'tmsai.revenue.line'
    _description = 'Revenue Line'
    _order = 'name'

    name = fields.Char('Description', required=True)

    # Links to parent documents
    fsd_id = fields.Many2one('tmsai.freight.settlement', 'Settlement', ondelete='cascade')
    fo_id = fields.Many2one('tmsai.freight.order', 'Freight Order', ondelete='cascade')
    fb_id = fields.Many2one('tmsai.freight.booking', 'Freight Booking', ondelete='cascade')

    # Product and pricing
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float('Quantity', digits=(12, 3), required=True, default=1.0)
    price_unit = fields.Float('Unit Price', digits=(12, 2), required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    taxes_id = fields.Many2many('account.tax', string='Taxes')

    # Computed amounts
    amount_subtotal = fields.Float('Subtotal', digits=(12, 2),
                                  compute='_compute_amounts', store=True)
    amount_total = fields.Float('Total', digits=(12, 2),
                               compute='_compute_amounts', store=True)

    # Rate and agreement references
    agreement_id = fields.Many2one('tmsai.freight.agreement', 'Agreement')
    rate_id = fields.Many2one('tmsai.freight.rate', 'Rate')
    accessorial_id = fields.Many2one('tmsai.accessorial', 'Accessorial')
    is_fuel_surcharge = fields.Boolean('Is Fuel Surcharge', default=False)

    # Calculation details
    calc_json = fields.Text('Calculation Details', readonly=True)

    # Cost accounting
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    @api.depends('quantity', 'price_unit', 'taxes_id')
    def _compute_amounts(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            line.amount_subtotal = subtotal

            # Calculate tax amount
            taxes = line.taxes_id.compute_all(line.price_unit, line.currency_id,
                                             line.quantity, product=line.product_id)
            line.amount_total = taxes['total_included']
