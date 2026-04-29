from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleApprovalConfiguration(models.Model):
    _name = "sale.approval.configuration"
    _description = "Sale Approval Configuration"
    _order = "sequence, id"

    user_id = fields.Many2one("res.users", required=True, string="Approver")
    sequence = fields.Integer(required=True, default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "sale_approval_configuration_user_unique",
            "unique(user_id)",
            "Approver must be unique in approval configuration.",
        )
    ]

    @api.constrains("sequence")
    def _check_sequence(self):
        for record in self:
            if record.sequence <= 0:
                raise ValidationError(_("Sequence must be greater than 0."))
