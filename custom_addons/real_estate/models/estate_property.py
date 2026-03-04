from odoo import models, fields

class estate_property(models.Model):
    _name="estate.property"
    _description="estate property"

    name=fields.Char(required=True)
    description=fields.Text()
    postcode=fields.Char()
    date_availability=fields.Date(default=fields.Date.add(fields.Date.today(), months=3),copy=False)
    expected_price=fields.Float(required=True)
    selling_price=fields.Float(copy=False)
    bedrooms=fields.Integer(default=2)
    living_area=fields.Integer()
    facades=fields.Integer()
    garage=fields.Boolean()
    garden=fields.Boolean()
    garden_area=fields.Integer()
    garden_orientation=fields.Selection(
        [
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        default='north',
        tracking=True
    )
    
    active=fields.Boolean(default=True)
    state=fields.Selection(
        [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        default='new',
        copy=False,
        required=True
    )