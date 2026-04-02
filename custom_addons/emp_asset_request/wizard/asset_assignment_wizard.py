from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError


class EmployeeAssetAssignmentWizard(models.TransientModel):
    _name = 'emp.asset.assignment.wizard'
    _description = 'Employee Asset Assignment Wizard'

    request_id = fields.Many2one(
        comodel_name='emp.asset.request',
        string='Request',
        required=True,
        readonly=True,
    )
    request_asset_model_id = fields.Many2one(
        related='request_id.asset_model_id',
        string='Requested Asset Type',
        readonly=True,
    )
    requested_quantity = fields.Integer(
        related='request_id.quantity',
        string='Requested Quantity',
        readonly=True,
    )
    asset_ids = fields.Many2many(
        comodel_name='account.asset',
        relation='emp_asset_assignment_wizard_asset_rel',
        column1='wizard_id',
        column2='asset_id',
        string='Assets to Assign',
        domain="[('state', '!=', 'model'), ('emp_asset_availability_state', '=', 'available'), ('model_id', '=', request_asset_model_id)]",
    )

    def action_confirm_assignment(self):
        self.ensure_one()
        request = self.request_id

        if not request.is_current_manager:
            raise UserError(_('Only the assigned manager can assign assets.'))
        if request.state != 'approved':
            raise UserError(_('Only approved requests can be assigned.'))

        if len(self.asset_ids) != request.quantity:
            raise ValidationError(_('You must select exactly %s assets.') % request.quantity)

        invalid_assets = self.asset_ids.filtered(
            lambda a: a.emp_asset_availability_state != 'available'
            or a.state == 'model'
            or a.model_id != request.asset_model_id
        )
        if invalid_assets:
            raise ValidationError(_('Some selected assets are no longer available or do not match the requested type.'))

        now = fields.Datetime.now()
        self.asset_ids.write({
            'emp_asset_availability_state': 'assigned',
            'emp_assigned_employee_id': request.employee_id.id,
            'emp_assigned_request_id': request.id,
            'emp_assignment_date': now,
        })

        request.write({
            'state': 'assigned',
            'assignment_date': now,
            'assigned_asset_ids': [(6, 0, self.asset_ids.ids)],
        })
        asset_names = ', '.join(str(name) for name in self.asset_ids.mapped('name'))
        request.message_post(body=_('Assets assigned: %s') % asset_names)

        return {'type': 'ir.actions.act_window_close'}
