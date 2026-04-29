from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ApprovalConfiguration(models.Model):
    _name = "approval.configuration"
    _description = "Approval Configuration"
    _order = "amount_from, id"

    amount_from = fields.Float(required=True)
    amount_to = fields.Float(required=True)
    approval_role = fields.Selection(
        [("manager", "Manager"), ("director", "Director")],
        required=True,
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "approval_configuration_no_duplicate",
            "unique(amount_from, amount_to, approval_role)",
            "Duplicate approval configuration is not allowed.",
        ),
    ]

    @api.constrains("amount_from", "amount_to")
    def _check_amount_range(self):
        for rec in self:
            if rec.amount_from <= 0 or rec.amount_to <= 0:
                raise ValidationError(_("Amount From and Amount To must be greater than 0."))
            if rec.amount_from >= rec.amount_to:
                raise ValidationError(_("Amount From must be less than Amount To."))

    @api.constrains("amount_from", "amount_to", "active")
    def _check_overlap(self):
        for rec in self.filtered("active"):
            domain = [
                ("id", "!=", rec.id),
                ("active", "=", True),
                ("amount_from", "<", rec.amount_to),
                ("amount_to", ">", rec.amount_from),
            ]
            if self.search_count(domain):
                raise ValidationError(
                    _("Overlapping amount ranges are not allowed in active configurations.")
                )
