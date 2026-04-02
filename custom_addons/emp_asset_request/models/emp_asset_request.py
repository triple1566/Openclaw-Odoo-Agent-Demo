# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class EmployeeAssetRequest(models.Model):
    _name = 'emp.asset.request'
    _description = 'Employee Asset Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Request Number',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        readonly=True,
        tracking=True,
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self._default_employee_id(),
        readonly=True,
        tracking=True,
    )
    manager_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Manager',
        compute='_compute_manager_id',
        store=True,
        readonly=True,
        tracking=True,
    )
    manager_user_id = fields.Many2one(
        related='manager_id.user_id',
        string='Manager User',
        store=True,
        readonly=True,
    )
    asset_model_id = fields.Many2one(
        comodel_name='account.asset',
        string='Asset Type',
        required=True,
        domain="[('state', '=', 'model')]",
        tracking=True,
    )
    quantity = fields.Integer(
        string='Quantity',
        required=True,
        default=1,
        tracking=True,
    )
    reason = fields.Text(
        string='Reason',
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('assigned', 'Assigned'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    assignment_date = fields.Datetime(
        string='Assignment Date',
        readonly=True,
        copy=False,
        tracking=True,
    )
    assigned_asset_ids = fields.Many2many(
        comodel_name='account.asset',
        relation='emp_asset_request_asset_rel',
        column1='request_id',
        column2='asset_id',
        string='Assigned Assets',
        readonly=True,
        copy=False,
    )
    is_current_manager = fields.Boolean(
        compute='_compute_is_current_manager',
        string='Is Current Manager',
    )

    @api.model
    def _get_current_employee(self):
        employee = self.env.user.employee_id
        if not employee:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
        return employee

    @api.model
    def _default_employee_id(self):
        employee = self._get_current_employee()
        return employee.id

    @api.depends('employee_id')
    def _compute_manager_id(self):
        for request in self:
            request.manager_id = request.employee_id.parent_id

    @api.depends('manager_user_id')
    def _compute_is_current_manager(self):
        for request in self:
            request.is_current_manager = bool(request.manager_user_id and request.manager_user_id.id == self.env.uid)

    @api.constrains('quantity')
    def _check_quantity(self):
        for request in self:
            if request.quantity < 1:
                raise ValidationError(_('Requested quantity must be at least 1.'))

    def _check_request_owner_on_create(self, vals):
        current_employee = self._get_current_employee()
        if not current_employee:
            raise ValidationError(_('Your user is not linked to an employee. Please contact HR.'))
        if vals.get('employee_id') and vals.get('employee_id') != current_employee.id:
            raise ValidationError(_('You can only create an asset request for yourself.'))

    def _check_request_owner_on_write(self, vals):
        current_employee = self._get_current_employee()
        if not current_employee:
            raise ValidationError(_('Your user is not linked to an employee. Please contact HR.'))
        if 'employee_id' in vals and vals['employee_id'] != current_employee.id:
            raise ValidationError(_('You cannot change the employee on this request.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_request_owner_on_create(vals)
            if not vals.get('employee_id'):
                vals['employee_id'] = self._get_current_employee().id
            if not vals.get('name') or vals.get('name') == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('emp.asset.request') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        for request in self:
            request._check_request_owner_on_write(vals)
        return super().write(vals)

    def action_submit(self):
        for request in self:
            if request.state != 'draft':
                continue
            if not request.manager_id or not request.manager_user_id:
                raise UserError(_('A manager with a linked user is required before submitting.'))
            request.write({'state': 'submitted'})
            request.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=request.manager_user_id.id,
                summary=_('Approve asset request %s') % request.name,
                note=_('Please review and approve or reject this asset request.'),
            )
            request.message_post(
                body=_('Asset request submitted for approval.'),
                partner_ids=[request.manager_user_id.partner_id.id],
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )

    def _check_manager_authority(self):
        for request in self:
            if not request.is_current_manager:
                raise UserError(_('Only the assigned manager can perform this action.'))

    def action_approve(self):
        self._check_manager_authority()
        for request in self:
            if request.state != 'submitted':
                continue
            request.write({'state': 'approved'})
            request.activity_feedback(['mail.mail_activity_data_todo'], feedback=_('Request approved.'))
            request.message_post(body=_('Asset request approved.'))

    def action_reject(self):
        self._check_manager_authority()
        for request in self:
            if request.state != 'submitted':
                continue
            request.write({'state': 'rejected'})
            request.activity_feedback(['mail.mail_activity_data_todo'], feedback=_('Request rejected.'))
            request.message_post(body=_('Asset request rejected.'))

    def action_open_assignment_wizard(self):
        self.ensure_one()
        self._check_manager_authority()
        if self.state != 'approved':
            raise UserError(_('Only approved requests can be assigned.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assign Assets'),
            'res_model': 'emp.asset.assignment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_request_id': self.id,
            },
        }
