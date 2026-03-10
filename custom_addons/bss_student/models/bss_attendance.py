# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BssAttendance(models.Model):
    _name = 'bss.attendance'
    _description = 'Attendance'
    _order = 'attendance_date desc'

    attendance_number = fields.Char(
        string='Attendance Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    student_id = fields.Many2one('bss.student', string='Student', required=True)
    attendance_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave')
    ], string='Status', required=True, default='present')
    checkin_time = fields.Datetime(string='Check-in Time')
    checkout_time = fields.Datetime(string='Check-out Time')

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-generate attendance number with format ATD/YYYY/MONTH/0001"""
        for vals in vals_list:
            if vals.get('attendance_number', _('New')) == _('New'):
                vals['attendance_number'] = self.env['ir.sequence'].next_by_code('bss.attendance') or _('New')
        return super(BssAttendance, self).create(vals_list)
