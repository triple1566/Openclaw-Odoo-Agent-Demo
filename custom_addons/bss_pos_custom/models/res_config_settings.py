from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_show_order_button = fields.Boolean(
        string="Show Order Button",
        related="pos_config_id.show_order_button",
        readonly=False
    )