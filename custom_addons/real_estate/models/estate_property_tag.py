from odoo import api, fields, models
from odoo.exceptions import ValidationError


class estate_property_tag(models.Model):
    _name = "estate.property.tag"
    _description = "estate property tag"
    _order = "name"

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            existing = self.search([
                ('name', '=', record.name),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(
                    "Property tag name must be unique."
                )

    name = fields.Char(required=True)
    color = fields.Integer()