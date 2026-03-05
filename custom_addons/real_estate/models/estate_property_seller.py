from odoo import fields, models


class estate_property_seller(models.Model):
    _name = "estate.property.seller"
    _description = "estate property seller"

    name = fields.Char(required=True)