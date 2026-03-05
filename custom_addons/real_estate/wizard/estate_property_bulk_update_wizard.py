from odoo import fields, models


class EstatePropertyBulkUpdateWizard(models.TransientModel):
    _name = "estate.property.bulk.update.wizard"
    _description = "Bulk Update Expected Price Wizard"

    percentage = fields.Float(string="Percentage", required=True)

    def action_apply_bulk_update(self):
        active_ids = self.env.context.get("active_ids", [])
        properties = self.env["estate.property"].browse(active_ids)
        for record in properties:
            record.expected_price = record.expected_price * (1 + (self.percentage / 100.0))
        return {"type": "ir.actions.act_window_close"}
