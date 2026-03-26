from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    show_order_source_button = fields.Boolean(
        compute="_compute_show_order_source_button"
    )

    def _compute_show_order_source_button(self):
        # SUDO METHOD USED TO GET THE PARAMETER VALUE bypasses permissions and record rules
        param = self.env["ir.config_parameter"].sudo().get_param(
            "pos_order_source.show_order_button",
            default="False",
        )
        enabled = param == "True"
        for config in self:
            config.show_order_source_button = enabled