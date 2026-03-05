from odoo import api, fields, models
from odoo.exceptions import ValidationError

class estate_property_type(models.Model):
    _name="estate.property.type"
    _description="estate property type"
    _order = "sequence, name"

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            existing = self.search([
                ('name', '=', record.name),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(
                    "Property type name must be unique."
                )

    name=fields.Char(required=True)
    sequence=fields.Integer(default=1)
    property_ids = fields.One2many("estate.property", "property_type_id")