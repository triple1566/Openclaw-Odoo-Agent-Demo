# -*- coding: utf-8 -*-

from odoo import fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_from = fields.Selection(
        [
            ('online', 'Online'),
            ('offline', 'Offline')
        ],
        string="Order From",
        default='offline',
        readonly=True
    )
