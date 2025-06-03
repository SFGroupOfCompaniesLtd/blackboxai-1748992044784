# -*- coding: utf-8 -*-
# Copyright (C) Wisenetic Technologies.

from odoo import models
from odoo import api, fields



class PosProduct(models.Model):
    _inherit = 'product.product'

    qty_available = fields.Float(string="On Hand Quantity")
    virtual_available = fields.Float(string="Forecasted Quantity")

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        print(params,"............params")
        params += ['qty_available', 'virtual_available']
        return params
