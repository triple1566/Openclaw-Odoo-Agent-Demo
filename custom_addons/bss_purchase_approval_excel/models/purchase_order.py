from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    _TO_APPROVE_ALLOWED_WRITE_FIELDS = {
        "approval_state",
        "approval_role",
        "requester_id",
        "requested_datetime",
        "approver_id",
        "approved_datetime",
        "message_follower_ids",
        "message_ids",
        "activity_ids",
    }

    approval_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("to_approve", "To Approve"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        copy=False,
    )
    approval_role = fields.Selection(
        [("manager", "Manager"), ("director", "Director")],
        string="Pending Approval Role",
        copy=False,
        readonly=True,
    )
    vendor_address = fields.Char(related="partner_id.contact_address_complete", readonly=True)
    vendor_phone = fields.Char(related="partner_id.phone", readonly=True)
    requester_id = fields.Many2one("res.users", string="Requester", copy=False)
    requested_datetime = fields.Datetime(string="Requested Datetime", copy=False)
    approver_id = fields.Many2one("res.users", string="Approver", copy=False)
    approved_datetime = fields.Datetime(string="Approved Datetime", copy=False)
    approver_line_ids = fields.One2many(
        "purchase.order.approver", "order_id", string="Approvers", copy=False
    )

    def _check_manager_group(self):
        if not self.env.user.has_group("bss_purchase_approval_excel.group_purchase_manager"):
            raise AccessError(_("Only users in Purchase Manager group can perform this action."))

    def _get_approval_configuration_for_amount(self, amount_total):
        config = self.env["approval.configuration"].search(
            [
                ("active", "=", True),
                ("amount_from", "<=", amount_total),
                ("amount_to", ">=", amount_total),
            ],
            order="amount_from asc, id asc",
            limit=1,
        )
        if not config:
            raise UserError(
                _(
                    "No active approval configuration found for amount %(amount)s.",
                    amount=amount_total,
                )
            )
        return config

    def _get_approver_group_xmlid(self, approval_role):
        return {
            "manager": "bss_purchase_approval_excel.group_purchase_manager",
            "director": "bss_purchase_approval_excel.group_purchase_director",
        }.get(approval_role)

    def _get_approver_user_from_configuration(self, config):
        group_xmlid = self._get_approver_group_xmlid(config.approval_role)
        if not group_xmlid:
            raise UserError(_("Unsupported approval role in approval configuration."))

        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        if not group:
            raise UserError(_("Approval group not found for role: %s") % config.approval_role)

        user = self.env["res.users"].search(
            [
                ("active", "=", True),
                ("share", "=", False),
                ("group_ids", "in", group.id),
            ],
            order="id asc",
            limit=1,
        )
        if not user:
            raise UserError(
                _("No active user found in group %(group)s.", group=group.display_name)
            )
        if not user.partner_id.email:
            raise UserError(
                _(
                    "Approver %(user)s has no email address configured.",
                    user=user.display_name,
                )
            )
        return user

    def _send_approval_email(self, approver_user):
        self.ensure_one()
        email_sent, error = self._send_email(
            subject=_("Purchase Order %s Requires Your Approval") % self.name,
            email_to=approver_user.partner_id.email,
            body_html=_(
                """
                <p>Hello %(approver)s,</p>
                <p>Purchase Order <strong>%(po)s</strong> requires your approval.</p>
                <p>Vendor: %(vendor)s</p>
                <p>Total: %(amount)s</p>
                """,
                approver=approver_user.name,
                po=self.name,
                vendor=self.partner_id.display_name,
                amount=self.amount_total,
            ),
        )
        if not email_sent:
            self.message_post(
                body=_(
                    "Approval email could not be sent to %(approver)s. Reason: %(reason)s",
                    approver=approver_user.display_name,
                    reason=error or _("Unknown error"),
                )
            )

    def _send_email(self, subject, email_to, body_html):
        self.ensure_one()
        if not email_to:
            return False, _("Recipient email is empty.")

        email_from = (
            self.env.user.email_formatted
            or self.env.company.email
            or self.env.user.partner_id.email
            or "noreply@example.com"
        )

        mail_values = {
            "subject": subject,
            "email_to": email_to,
            "body_html": body_html,
            "author_id": self.env.user.partner_id.id,
            "email_from": email_from,
            "auto_delete": True,
        }
        try:
            mail = self.env["mail.mail"].sudo().create(mail_values)
            mail.sudo().send(raise_exception=False)

            if mail.state == "exception":
                return False, mail.failure_reason or _("SMTP delivery failed.")
            
            # Ensure mail is deleted after sending to prevent orphaned records
            if mail.state != "exception":
                mail.unlink()
            return True, False
        except Exception as e:
            return False, str(e)

    def _send_approval_reminder_email(self):
        self.ensure_one()
        if not self.approver_id or not self.approver_id.partner_id.email:
            return False
        email_sent, _error = self._send_email(
            subject=_("Reminder: Purchase Order %s is still awaiting approval") % self.name,
            email_to=self.approver_id.partner_id.email,
            body_html=_(
                """
                <p>Hello %(approver)s,</p>
                <p>This is a reminder that Purchase Order <strong>%(po)s</strong> has been waiting for approval for more than 3 days.</p>
                <p>Vendor: %(vendor)s</p>
                <p>Total: %(amount)s</p>
                """,
                approver=self.approver_id.name,
                po=self.name,
                vendor=self.partner_id.display_name,
                amount=self.amount_total,
            ),
        )
        return email_sent

    def _notify_requester(self, decision):
        self.ensure_one()
        if not self.requester_id:
            return

        decision_label = {
            "approved": _("Approved"),
            "rejected": _("Rejected"),
        }.get(decision, _("Updated"))
        decision_text = str(decision_label).lower()

        requester_email = self.requester_id.partner_id.email
        if requester_email:
            email_sent, error = self._send_email(
                subject=_("Purchase Order %s %s") % (self.name, decision_label),
                email_to=requester_email,
                body_html=_(
                    """
                    <p>Hello %(requester)s,</p>
                    <p>Your Purchase Order <strong>%(po)s</strong> has been <strong>%(decision)s</strong>.</p>
                    <p>Processed by: %(approver)s</p>
                    """,
                    requester=self.requester_id.name,
                    po=self.name,
                    decision=decision_text,
                    approver=self.env.user.display_name,
                ),
            )
            if not email_sent:
                self.message_post(
                    body=_(
                        "Requester notification email failed. Reason: %(reason)s",
                        reason=error or _("Unknown error"),
                    )
                )

    def _log_approval_action(self, action):
        self.ensure_one()
        messages = {
            "submitted": _(
                "Submitted for approval by %(user)s.",
                user=self.env.user.display_name,
            ),
            "approved": _(
                "Approved by %(user)s.",
                user=self.env.user.display_name,
            ),
            "rejected": _(
                "Rejected by %(user)s.",
                user=self.env.user.display_name,
            ),
            "reminder_sent": _(
                "Reminder sent to approver %(approver)s.",
                approver=self.approver_id.display_name if self.approver_id else _("Unknown"),
            ),
            "reminder_skipped": _("Reminder triggered but approver email is missing."),
        }
        self.message_post(body=messages.get(action, _("Approval action logged.")))

    def _check_current_user_is_approver(self):
        for order in self:
            if order.approval_state != "to_approve":
                raise UserError(_("Only purchase orders in To Approve state can be processed."))
            if not order.approver_id:
                raise UserError(_("No approver is assigned to this purchase order."))
            if order.approver_id != self.env.user:
                raise AccessError(_("Only the assigned approver can perform this action."))

    def _validate_vendor_contact_info(self):
        for order in self:
            partner = order.partner_id
            if not partner:
                continue
            if not partner.contact_address_complete or not partner.phone:
                raise UserError(
                    _("Vendor must have both address and phone before saving this Purchase Order.")
                )

    def action_submit_for_approval(self):
        self._check_manager_group()
        for order in self:
            config = order._get_approval_configuration_for_amount(order.amount_total)
            approver = order._get_approver_user_from_configuration(config)
            order.write(
                {
                    "approval_state": "to_approve",
                    "approval_role": config.approval_role,
                    "requester_id": self.env.user.id,
                    "requested_datetime": fields.Datetime.now(),
                    "approver_id": approver.id,
                    "approved_datetime": False,
                }
            )
            order._send_approval_email(approver)
            order._log_approval_action("submitted")

    def action_mark_approved(self):
        self._check_current_user_is_approver()
        for order in self:
            order.write(
                {
                    "approval_state": "approved",
                    "approval_role": False,
                    "approver_id": self.env.user.id,
                    "approved_datetime": fields.Datetime.now(),
                }
            )
            order._log_approval_action("approved")
            order._notify_requester("approved")

    def action_mark_rejected(self):
        self._check_current_user_is_approver()
        for order in self:
            order.write(
                {
                    "approval_state": "rejected",
                    "approval_role": False,
                    "approver_id": self.env.user.id,
                    "approved_datetime": False,
                }
            )
            order._log_approval_action("rejected")
            order._notify_requester("rejected")

    def action_reset_to_draft(self):
        self._check_manager_group()
        for order in self:
            order.write(
                {
                    "approval_state": "draft",
                    "approval_role": False,
                    "requester_id": False,
                    "requested_datetime": False,
                    "approver_id": False,
                    "approved_datetime": False,
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._validate_vendor_contact_info()
        return orders

    def write(self, vals):
        blocked_fields = set(vals) - self._TO_APPROVE_ALLOWED_WRITE_FIELDS
        if blocked_fields and any(order.approval_state == "to_approve" for order in self):
            raise UserError(_("All fields are read-only while approval state is To Approve."))

        result = super().write(vals)
        self._validate_vendor_contact_info()
        return result

    def button_confirm(self):
        for order in self:
            if order.approval_state != "approved":
                raise UserError(
                    _("Purchase Order cannot be confirmed unless approval state is Approved.")
                )
        return super().button_confirm()

    @api.model
    def _cron_send_approval_reminders(self):
        threshold = fields.Datetime.now() - timedelta(days=3)
        orders = self.search(
            [
                ("state", "in", ["draft", "sent"]),
                ("approval_state", "=", "to_approve"),
                ("requested_datetime", "!=", False),
                ("requested_datetime", "<=", fields.Datetime.to_string(threshold)),
            ]
        )

        for order in orders:
            email_sent = order._send_approval_reminder_email()
            if email_sent:
                order._log_approval_action("reminder_sent")
            else:
                order._log_approval_action("reminder_skipped")

    @api.model
    def _cron_cleanup_mail_records(self):
        """Clean up orphaned or failed mail.mail records to prevent stale references."""
        mail_model = self.env["mail.mail"]
        try:
            # Delete failed emails older than 1 day
            threshold = fields.Datetime.now() - timedelta(days=1)
            failed_mails = mail_model.search(
                [
                    ("state", "=", "exception"),
                    ("create_date", "<=", fields.Datetime.to_string(threshold)),
                ]
            )
            if failed_mails:
                failed_mails.unlink()
                self.env.cr.commit()
        except Exception as e:
            _logger = self.env["ir.logging"]
            _logger.create(
                {
                    "name": "Mail Cleanup Error",
                    "type": "server",
                    "level": "warning",
                    "message": str(e),
                }
            )


class PurchaseOrderApprover(models.Model):
    _name = "purchase.order.approver"
    _description = "Purchase Order Approver"
    _order = "sequence, id"

    order_id = fields.Many2one("purchase.order", required=True, ondelete="cascade")
    user_id = fields.Many2one("res.users", string="Approver", required=True)
    sequence = fields.Integer(default=10)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("refused", "Refused"),
        ],
        default="pending",
        copy=False,
        required=True,
    )
    action_date = fields.Datetime(copy=False)
