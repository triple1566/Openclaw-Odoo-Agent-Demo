from odoo import _, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    low_stock_min_qty = fields.Float(
        string='Minimum Stock Level',
        default=0.0,
        help='Daily alert will trigger when the available quantity is at or below this level.',
    )
    low_stock_alert_sent = fields.Boolean(
        string='Low Stock Alert Sent',
        default=False,
        copy=False,
    )

    def _cron_low_stock_alert(self):
        products = self.with_context(active_test=False).search(
            [
                ('type', '!=', 'service'),
                ('low_stock_min_qty', '>', 0.0),
            ]
        )
        if not products:
            return

        stock_manager_partners = self.env.ref('stock.group_stock_manager').users.mapped('partner_id')

        for product in products:
            qty = product.qty_available
            if qty <= product.low_stock_min_qty:
                if not product.low_stock_alert_sent:
                    product.message_post(
                        body=_(
                            'Low stock alert for %(product)s: available quantity %(qty).2f is at or below minimum level %(min_qty).2f.'
                        ) % {
                            'product': product.display_name,
                            'qty': qty,
                            'min_qty': product.low_stock_min_qty,
                        },
                        partner_ids=stock_manager_partners.ids,
                    )
                    product.sudo().write({'low_stock_alert_sent': True})
            elif product.low_stock_alert_sent:
                product.sudo().write({'low_stock_alert_sent': False})