from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    order_from = fields.Selection(
        [
            ("online", "Online"),
            ("offline", "Offline"),
        ],
        string="Order From",
        default="offline",
        readonly=True,
    )

    @classmethod
    def order_fields(cls, ui_order):
        vals = super().order_fields(ui_order)
        vals['order_from'] = ui_order.get('order_from', 'offline')
        return vals
