from odoo import fields, models, api

class rank_configuration(models.Model):
    # This class represents a single rank object,
    # Where there are multiple rank objects that can be 
    # assigned to a customer.

    _name = "rank.configuration"
    _description = "Rank Config model for the BSS sales customization module."

    rank_name = fields.Char(required=True)
    rank_code = fields.Integer(required=True)

    # If another rank object has default_rank = True
    # all other rank object must be default_rank = False
    default_rank = fields.Boolean(required=True)
    status = fields.Selection(
        [
            ('active', 'Active'),
            ('deactive', 'Deactive')
        ],
        required=True
    )
    discount_percentage = fields.Float(required=True)