from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ApprovalRoleAssignment(models.Model):
    _name = "approval.role.assignment"
    _description = "Approval Role Assignment"
    _order = "approval_role, user_id"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
        domain=[("share", "=", False)],
    )
    approval_role = fields.Selection(
        [("manager", "Manager"), ("director", "Director")],
        string="Approval Role",
        required=True,
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "approval_role_assignment_unique_user",
            "unique(user_id)",
            "Each user can have only one purchase approval role.",
        )
    ]

    def _get_role_group(self):
        self.ensure_one()
        group_xmlid = {
            "manager": "bss_purchase_approval_excel.group_purchase_manager",
            "director": "bss_purchase_approval_excel.group_purchase_director",
        }.get(self.approval_role)
        if not group_xmlid:
            raise UserError(_("Unsupported approval role: %s") % self.approval_role)

        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        if not group:
            raise UserError(_("Approval group not found for role: %s") % self.approval_role)
        return group

    def _sync_user_groups(self):
        manager_group = self.env.ref(
            "bss_purchase_approval_excel.group_purchase_manager", raise_if_not_found=False
        )
        director_group = self.env.ref(
            "bss_purchase_approval_excel.group_purchase_director", raise_if_not_found=False
        )
        if not manager_group or not director_group:
            raise UserError(_("Approval groups are not fully configured."))

        for assignment in self:
            commands = [(3, manager_group.id), (3, director_group.id)]
            if assignment.active:
                commands.append((4, assignment._get_role_group().id))
            assignment.user_id.sudo().write({"group_ids": commands})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_user_groups()
        return records

    def write(self, vals):
        previous_users = {record.id: record.user_id.sudo() for record in self}
        result = super().write(vals)
        manager_group = self.env.ref(
            "bss_purchase_approval_excel.group_purchase_manager", raise_if_not_found=False
        )
        director_group = self.env.ref(
            "bss_purchase_approval_excel.group_purchase_director", raise_if_not_found=False
        )
        if not manager_group or not director_group:
            raise UserError(_("Approval groups are not fully configured."))

        for record in self:
            previous_user = previous_users.get(record.id)
            if previous_user and previous_user.id != record.user_id.id:
                previous_user.write({"group_ids": [(3, manager_group.id), (3, director_group.id)]})
        self._sync_user_groups()
        return result

    def unlink(self):
        manager_group = self.env.ref(
            "bss_purchase_approval_excel.group_purchase_manager", raise_if_not_found=False
        )
        director_group = self.env.ref(
            "bss_purchase_approval_excel.group_purchase_director", raise_if_not_found=False
        )
        if not manager_group or not director_group:
            raise UserError(_("Approval groups are not fully configured."))

        self.mapped("user_id").sudo().write(
            {"groups_id": [(3, manager_group.id), (3, director_group.id)]}
        )
        return super().unlink()