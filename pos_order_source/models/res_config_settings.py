from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_order_source_button_setting = fields.Boolean(
        string="Show Order Source Button",
        config_parameter="pos_order_source.show_order_button",
    )