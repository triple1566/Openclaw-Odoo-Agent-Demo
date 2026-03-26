# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    show_order_button = fields.Boolean(string="Show Order Button")
