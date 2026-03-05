from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    sold_property_ids = fields.Many2many(
        "estate.property",
        compute="_compute_sold_property_ids",
        string="Sold Properties",
    )

    @api.depends("partner_id")
    def _compute_sold_property_ids(self):
        property_model = self.env["estate.property"]
        for user in self:
            if not user.partner_id:
                user.sold_property_ids = False
                continue
            user.sold_property_ids = property_model.search([
                ("seller", "=", user.partner_id.id),
                ("state", "=", "sold"),
            ])
