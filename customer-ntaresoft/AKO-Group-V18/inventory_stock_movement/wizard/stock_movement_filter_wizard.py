from odoo import models, fields, api

class StockMovementFilterWizard(models.TransientModel):
    _name = 'stock.movement.filter.wizard'
    _description = 'Stock Movement Filter Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    product_id = fields.Many2one('product.product', string='Product')
    product_categ_id = fields.Many2one('product.category', string='Product Category')
    location_ids = fields.Many2many('stock.location', string='Locations')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

    def action_view_report(self):
        self.ensure_one()
        domain = []
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        elif self.product_categ_id:
            domain.append(('product_id.categ_id', '=', self.product_categ_id.id))
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))
        if self.warehouse_id:
            # Filter locations by warehouse
            warehouse_locations = self.env['stock.location'].search([('warehouse_id', '=', self.warehouse_id.id)])
            domain.append(('location_id', 'in', warehouse_locations.ids))

        # Pass filter parameters to context for report
        context = dict(self.env.context or {})
        context.update({
            'start_date': self.start_date,
            'end_date': self.end_date,
            'domain': domain,
        })

        return {
            'name': 'Inventory Stock Movement Report',
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.stock.movement.report',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': context,
            'domain': domain,
        }
