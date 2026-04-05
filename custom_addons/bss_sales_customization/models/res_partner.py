from odoo import models, fields, api
from odoo.exceptions import ValidationError

class res_partner(models.Model):
    _inherit="res.partner"

    rank_code = fields.Many2one("rank.configuration", string="Current Rank")

    # Operates on the model level
    @api.model
    def create(self, vals):
        record = super().create(vals)

        # search for a default rank
        default_rank = self.env['rank.configuration'].search(
            [('default_rank','=', True)],
            limit=1
        )

        # if for some reason, a default rank is not set, raise an error
        if not default_rank:
            raise ValidationError("No default rank is set. Set a default rank first, then try again.")
        
        record.rank_code = default_rank.rank_code

        return record
