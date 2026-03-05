from odoo import fields, models
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def set_property_sold(self):
        result = super().set_property_sold()
        for record in self:
            if not record.buyer:
                raise UserError("A buyer is required to create an invoice.")

            self.env["account.move"].create(
                {
                    "partner_id": record.buyer.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        fields.Command.create(
                            {
                                "name": "Real Estate Agency Fees (6%)",
                                "quantity": 1.0,
                                "price_unit": record.selling_price * 0.06,
                            }
                        ),
                        fields.Command.create(
                            {
                                "name": "Administrative Fees",
                                "quantity": 1.0,
                                "price_unit": 100.0,
                            }
                        ),
                    ],
                }
            )
        return result
