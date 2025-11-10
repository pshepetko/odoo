
from odoo import api, fields, models
from odoo.tools.translate import _


class TmsaiFreightSettlement(models.Model):
    _name = 'tmsai.freight.settlement'
    _description = 'Freight Settlement Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    name = fields.Char('Reference', required=True, copy=False, readonly=True,
                      default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                default=lambda self: self.env.company)

    # Links to FO or FB
    fo_id = fields.Many2one('tmsai.freight.order', 'Freight Order')
    fb_id = fields.Many2one('tmsai.freight.booking', 'Freight Booking')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)

    # Financial lines
    cost_line_ids = fields.One2many('tmsai.cost.line', 'fsd_id', 'Cost Lines')
    revenue_line_ids = fields.One2many('tmsai.revenue.line', 'fsd_id', 'Revenue Lines')

    # Computed totals
    totals_cost = fields.Float('Total Cost', digits=(12, 2),
                               compute='_compute_totals', store=True)
    totals_revenue = fields.Float('Total Revenue', digits=(12, 2),
                                 compute='_compute_totals', store=True)
    margin = fields.Float('Margin', digits=(12, 2),
                         compute='_compute_totals', store=True)

    # Accounting links
    vendor_bill_id = fields.Many2one('account.move', 'Vendor Bill')
    customer_invoice_id = fields.Many2one('account.move', 'Customer Invoice')
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('billed_vendor', 'Billed Vendor'),
        ('billed_customer', 'Billed Customer'),
        ('paid', 'Paid'),
    ], 'State', default='draft', tracking=True, index=True)

    notes = fields.Text('Notes', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tmsai.fsd') or _('New')
        return super().create(vals)

    @api.depends('cost_line_ids.amount_total', 'revenue_line_ids.amount_total')
    def _compute_totals(self):
        for fsd in self:
            total_cost = sum(line.amount_total for line in fsd.cost_line_ids if line.amount_total)
            total_revenue = sum(line.amount_total for line in fsd.revenue_line_ids if line.amount_total)

            fsd.totals_cost = total_cost
            fsd.totals_revenue = total_revenue
            fsd.margin = total_revenue - total_cost

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_create_vendor_bill(self):
        # Create vendor bill from cost lines
        self.write({'state': 'billed_vendor'})

    def action_create_customer_invoice(self):
        # Create customer invoice from revenue lines
        self.write({'state': 'billed_customer'})

    def action_mark_paid(self):
        self.write({'state': 'paid'})
