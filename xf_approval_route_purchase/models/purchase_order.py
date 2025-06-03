# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'approval.route.document']

    use_approval_route = fields.Selection(
        string="Use Approval Route",
        related='company_id.use_approval_route_purchase',
    )
    approval_route_id = fields.Many2one(
        readonly=True,
    )
    all_used_products = fields.Many2many(
        string='All Used Products',
        comodel_name='product.product',
        compute='_compute_all_used_products',
    )
    all_used_analytic_accounts = fields.Many2many(
        string='All Used Analytic Accounts',
        comodel_name='account.analytic.account',
        compute='_compute_all_used_analytic_accounts',
    )

    @api.depends('order_line.product_id')
    def _compute_all_used_products(self):
        for order in self:
            order.all_used_products = order.order_line.mapped('product_id')

    @api.depends('order_line.analytic_distribution')
    def _compute_all_used_analytic_accounts(self):
        for order in self:
            analytic_account_ids = []
            for line in order.order_line:
                if line.analytic_distribution:
                    aa_keys = line.analytic_distribution.keys()
                    for aa_key in aa_keys:
                        aa_ids = aa_key.split(',')
                        analytic_account_ids += list(map(int, aa_ids))
            order.all_used_analytic_accounts = list(set(analytic_account_ids))

    def button_approve(self, force=False):
        for order in self:
            if order.current_approval_stage_id:
                order._action_approve()
                if order._is_fully_approved():
                    super(PurchaseOrder, order).button_approve(force)
            else:
                # Do default behaviour if PO Team is not set
                super(PurchaseOrder, order).button_approve(force)
        return {}

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue

            if not order.approval_route_id:
                # Do default behaviour if PO Team is not set
                super(PurchaseOrder, order).button_confirm()
            else:
                # Generate approval route and send PO to approve
                order.generate_approval_route()
                if order.next_approval_stage_id:
                    # If approval route is generated and there is next approver mark the order "to approve"
                    order.write({'state': 'to approve'})
                    # And send request to approve
                    order._action_send_to_approve()
                else:
                    # If there are no approvers, do default behaviour and move PO to the "Purchase Order" state
                    super(PurchaseOrder, order).button_approve()

            order._add_supplier_to_product()
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def button_draft(self):
        """
        Clear approval stages and reset PO
        :return:
        """
        self._clear_approval_stages()
        return super(PurchaseOrder, self).button_draft()
