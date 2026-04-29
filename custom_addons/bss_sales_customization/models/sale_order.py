from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_line_ids = fields.One2many(
        "sale.order.approver", "order_id", string="Approvers", copy=False
    )
    approval_state = fields.Selection(
        [
            ("pending", "Pending Approval"),
            ("approved", "Approved"),
            ("refused", "Refused"),
        ],
        default="pending",
        copy=False,
        tracking=True,
    )

    def _get_rank_discount(self):
        self.ensure_one()
        rank = self.partner_id.rank_code
        return rank.discount_percentage if rank and rank.status == "active" else 0.0

    def _apply_rank_discount_to_lines(self):
        for order in self:
            discount = order._get_rank_discount() if order.partner_id else 0.0
            if order.order_line:
                order.order_line.write({"discount": discount})

    def _prepare_approval_lines(self):
        lines = []
        configs = self.env["sale.approval.configuration"].search(
            [("active", "=", True)], order="sequence, id"
        )
        for config in configs:
            lines.append(
                (
                    0,
                    0,
                    {
                        "user_id": config.user_id.id,
                        "sequence": config.sequence,
                        "state": "pending",
                    },
                )
            )
        return lines

    def _reset_approval_progress(self):
        for order in self:
            if order.approval_line_ids:
                order.approval_line_ids.write({"state": "pending", "action_date": False})
            order.approval_state = "pending"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("approval_line_ids"):
                vals["approval_line_ids"] = self._prepare_approval_lines()

        orders = super().create(vals_list)
        orders._apply_rank_discount_to_lines()
        orders._reset_approval_progress()
        return orders

    def write(self, vals):
        partner_changed = "partner_id" in vals
        line_changed = "order_line" in vals

        res = super().write(vals)

        if partner_changed or line_changed:
            self._apply_rank_discount_to_lines()
        if partner_changed:
            self._reset_approval_progress()

        return res

    @api.onchange("partner_id")
    def _onchange_partner_id_apply_rank_discount(self):
        for order in self:
            discount = order._get_rank_discount() if order.partner_id else 0.0
            for line in order.order_line:
                line.discount = discount

    def _check_all_approved(self):
        self.ensure_one()
        if not self.approval_line_ids:
            return True
        return all(line.state == "approved" for line in self.approval_line_ids)

    def action_confirm(self):
        for order in self:
            if order.approval_state == "refused":
                raise UserError(
                    _("This quotation was refused by an approver and has been cancelled.")
                )
            if not order._check_all_approved():
                raise UserError(
                    _("You can only confirm after all approvers have approved in sequence.")
                )
            order.approval_state = "approved"
        return super().action_confirm()

    def action_reset_to_draft(self):
        for order in self:
            if order.state == "cancel":
                order.action_draft()
            else:
                order.write({"state": "draft"})
            order._reset_approval_progress()


class SaleOrderApprover(models.Model):
    _name = "sale.order.approver"
    _description = "Sale Order Approver"
    _order = "sequence, id"

    order_id = fields.Many2one("sale.order", required=True, ondelete="cascade")
    user_id = fields.Many2one("res.users", required=True)
    sequence = fields.Integer(default=10)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("refused", "Refused"),
        ],
        default="pending",
        required=True,
        copy=False,
    )
    action_date = fields.Datetime(copy=False)

    def _get_previous_unapproved_lines(self):
        self.ensure_one()
        return self.order_id.approval_line_ids.filtered(
            lambda line: line.sequence < self.sequence and line.state != "approved"
        )

    def action_approve(self):
        now = fields.Datetime.now()
        current_user = self.env.user
        for line in self:
            if line.user_id != current_user:
                raise UserError(_("Only the assigned approver can approve this step."))
            if line.state != "pending":
                raise UserError(_("This approval step is already processed."))
            if line._get_previous_unapproved_lines():
                raise UserError(_("You must wait for previous approvers to complete first."))

            line.write({"state": "approved", "action_date": now})
            if line.order_id._check_all_approved():
                line.order_id.approval_state = "approved"

    def action_refuse(self):
        now = fields.Datetime.now()
        current_user = self.env.user
        for line in self:
            if line.user_id != current_user:
                raise UserError(_("Only the assigned approver can refuse this step."))
            if line.state != "pending":
                raise UserError(_("This approval step is already processed."))
            if line._get_previous_unapproved_lines():
                raise UserError(_("You must wait for previous approvers to complete first."))

            line.write({"state": "refused", "action_date": now})
            line.order_id.approval_state = "refused"
            line.order_id.action_cancel()
