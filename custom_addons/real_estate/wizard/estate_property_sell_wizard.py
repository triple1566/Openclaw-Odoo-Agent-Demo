from odoo import fields, models


class EstatePropertySellWizard(models.TransientModel):
    _name = "estate.property.sell.wizard"
    _description = "Estate Property Sell Wizard"

    property_id = fields.Many2one("estate.property", required=True, readonly=True)
    note = fields.Char(string="Note")

    def action_confirm_sale(self):
        self.ensure_one()
        self.property_id.set_property_sold()
        return {"type": "ir.actions.act_window_close"}
