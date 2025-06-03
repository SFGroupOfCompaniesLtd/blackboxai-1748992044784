from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class InventoryStockMovementReport(models.Model):
    _name = 'inventory.stock.movement.report'
    _description = 'Inventory Stock Movement Report'
    _auto = False
    _order = 'product_id, location_id'

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    location_id = fields.Many2one('stock.location', string='Location', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    opening_qty = fields.Float(string='Opening Quantity', readonly=True)
    incoming_qty = fields.Float(string='Incoming Quantity', readonly=True)
    outgoing_qty = fields.Float(string='Outgoing Quantity', readonly=True)
    internal_transfers = fields.Float(string='Internal Transfers', readonly=True)
    adjustments = fields.Float(string='Adjustments', readonly=True)
    closing_qty = fields.Float(string='Closing Quantity', readonly=True)

    @api.model
    def init(self):
        # Create or replace the SQL view for the report
        self.env.cr.execute("""
            DROP VIEW IF EXISTS inventory_stock_movement_report;
            CREATE OR REPLACE VIEW inventory_stock_movement_report AS (
                SELECT
                    row_number() OVER () AS id,
                    sm.product_id,
                    sm.location_id,
                    sm.company_id,
                    pt.uom_id,
                    COALESCE(SUM(CASE WHEN sm.date < current_date THEN sm.product_qty ELSE 0 END), 0) AS opening_qty,
                    COALESCE(SUM(CASE WHEN sm.date >= current_date AND sm.date <= current_date THEN
                        CASE WHEN sm.picking_type_id IN (SELECT id FROM stock_picking_type WHERE code = 'incoming') THEN sm.product_qty ELSE 0 END ELSE 0 END), 0) AS incoming_qty,
                    COALESCE(SUM(CASE WHEN sm.date >= current_date AND sm.date <= current_date THEN
                        CASE WHEN sm.picking_type_id IN (SELECT id FROM stock_picking_type WHERE code = 'outgoing') THEN sm.product_qty ELSE 0 END ELSE 0 END), 0) AS outgoing_qty,
                    COALESCE(SUM(CASE WHEN sm.location_id IN (SELECT id FROM stock_location WHERE usage = 'internal')
                        AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage = 'internal') THEN sm.product_qty ELSE 0 END), 0) AS internal_transfers,
                    COALESCE(SUM(CASE WHEN sm.location_id = sm.location_dest_id THEN sm.product_qty ELSE 0 END), 0) AS adjustments,
                    0.0 AS closing_qty
                FROM stock_move sm
                JOIN product_product pp ON sm.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                GROUP BY sm.product_id, sm.location_id, sm.company_id, pt.uom_id
            )
        """)

    @api.model
    def get_report_data(self, start_date, end_date, company_id=None, product_ids=None, location_ids=None, warehouse_id=None):
        # This method will be used by the wizard to fetch filtered data
        domain = [('date', '>=', start_date), ('date', '<=', end_date)]
        if company_id:
            domain.append(('company_id', '=', company_id))
        if product_ids:
            domain.append(('product_id', 'in', product_ids))
        if location_ids:
            domain.append(('location_id', 'in', location_ids))
        # warehouse filter can be implemented by filtering locations belonging to warehouse
        moves = self.env['stock.move'].search(domain)
        # Aggregate data as per logic
        # This is a placeholder for actual aggregation logic
        return moves
