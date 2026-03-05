from odoo import fields, models


class estate_property_buyer(models.Model):
    _name = "estate.property.buyer"
    _description = "estate property buyer"

    name = fields.Char(required=True)