# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    emp_asset_availability_state = fields.Selection(
        selection=[('available', 'Available'), ('assigned', 'Assigned')],
        string='Availability',
        default='available',
        tracking=True,
        copy=False,
    )
    emp_assigned_employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Assigned Employee',
        copy=False,
    )
    emp_assigned_request_id = fields.Many2one(
        comodel_name='emp.asset.request',
        string='Asset Request',
        copy=False,
    )
    emp_assignment_date = fields.Datetime(
        string='Assignment Date',
        copy=False,
    )
