from odoo import _, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    low_stock_alert_sent = fields.Boolean(
        string='Low Stock Alert Sent',
        default=False,
        copy=False,
    )

    #inventory low stock alert cron job
    def _cron_low_stock_alert(self):
        threshold = 10.0

        products = self.with_context(active_test=False).search(
            [
                ('type', '!=', 'service'),
            ]
        )
        if not products:
            return

        stock_manager_partners = self.env.ref('stock.group_stock_manager').users.mapped('partner_id')

        for product in products:
            qty = product.qty_available
            if qty <= threshold:
                if not product.low_stock_alert_sent:
                    product.message_post(
                        body=_(
                            'Low stock alert for %(product)s: available quantity %(qty).2f is at or below minimum level %(min_qty).2f.'
                        ) % {
                            'product': product.display_name,
                            'qty': qty,
                            'min_qty': threshold,
                        },
                        partner_ids=stock_manager_partners.ids,
                    )
                    product.sudo().write({'low_stock_alert_sent': True})
            elif product.low_stock_alert_sent:
                product.sudo().write({'low_stock_alert_sent': False})