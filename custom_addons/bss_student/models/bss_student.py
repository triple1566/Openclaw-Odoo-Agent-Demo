# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import ValidationError
from datetime import date


class BssStudent(models.Model):
    _name = 'bss.student'
    _description = 'Student'
    _rec_name = 'name'

    name = fields.Char(string='Student Name', required=True)
    student_number = fields.Char(
        string='Student Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    dob = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    roll_number = fields.Char(string='Roll Number')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    photo = fields.Binary(string='Photo')
    class_id = fields.Many2one('bss.class', string='Class')
    subject_ids = fields.Many2many(
        'bss.subject',
        'student_subject_rel',
        'student_id',
        'subject_id',
        string='Subjects'
    )
    attendance_ids = fields.One2many(
        'bss.attendance',
        'student_id',
        string='Attendance Records'
    )
    partner_id = fields.Many2one('res.partner', string='Related Contact', readonly=True)
    user_id = fields.Many2one('res.users', string='Related User', readonly=True, copy=False)

    _sql_constraints = [
        ('roll_number_unique', 'UNIQUE(roll_number)', 'Roll number must be unique!')
    ]

    @api.depends('dob')
    def _compute_age(self):
        """Calculate age from date of birth"""
        for record in self:
            if record.dob:
                today = date.today()
                dob = record.dob
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                record.age = age
            else:
                record.age = 0

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-generate student number and create related partner and user"""
        for vals in vals_list:
            if vals.get('student_number', _('New')) == _('New'):
                vals['student_number'] = self.env['ir.sequence'].next_by_code('bss.student') or _('New')

        students = super(BssStudent, self).create(vals_list)
        students._create_or_update_partner()
        students._create_or_link_user()
        return students

    def write(self, vals):
        """Update related partner when student is updated"""
        res = super(BssStudent, self).write(vals)
        if any(field in vals for field in ['name', 'email', 'phone']):
            self._create_or_update_partner()
        return res

    def _create_or_update_partner(self):
        """Create or update related res.partner"""
        for student in self:
            partner_vals = {
                'name': student.name,
                'email': student.email or False,
                'phone': student.phone or False,
                'is_student': True,
                'student_id': student.id,
            }
            
            if student.partner_id:
                # Update existing partner
                student.partner_id.write(partner_vals)
            else:
                # Create new partner
                partner = self.env['res.partner'].create(partner_vals)
                student.partner_id = partner.id

    def _get_unique_login(self):
        """Build a unique login for a student user."""
        self.ensure_one()

        base_login = (self.email or self.student_number or f'student_{self.id}' or '').strip().lower()
        if not base_login:
            base_login = f'student_{self.id}'

        users = self.env['res.users'].sudo()
        if not users.search_count([('login', '=', base_login)]):
            return base_login

        suffix = 1
        while True:
            candidate = f'{base_login}.{suffix}'
            if not users.search_count([('login', '=', candidate)]):
                return candidate
            suffix += 1

    def _create_or_link_user(self):
        """Create or link res.users using the student's auto-created partner."""
        users = self.env['res.users'].sudo().with_context(no_reset_password=True)
        student_user_group = self.env.ref('bss_student_access_right.group_student_user', raise_if_not_found=False)
        for student in self:
            if not student.partner_id:
                continue

            existing_user = users.search([('partner_id', '=', student.partner_id.id)], limit=1)
            if existing_user:
                if student_user_group:
                    existing_user.write({'group_ids': [Command.link(student_user_group.id)]})
                student.user_id = existing_user.id
                continue

            user_vals = {
                'name': student.name,
                'login': student._get_unique_login(),
                'partner_id': student.partner_id.id,
            }
            if student_user_group:
                user_vals['group_ids'] = [Command.link(student_user_group.id)]
            new_user = users.create(user_vals)
            student.user_id = new_user.id

    @api.onchange('class_id')
    def _onchange_class_id(self):
        """Auto-fill subjects when class is selected"""
        if self.class_id:
            self.subject_ids = [(6, 0, self.class_id.subject_ids.ids)]
        else:
            self.subject_ids = [(5, 0, 0)]

    @api.constrains('roll_number')
    def _check_roll_number(self):
        """Validate roll number"""
        for record in self:
            if record.roll_number and not record.roll_number.strip():
                raise ValidationError(_('Roll number cannot be empty or whitespace only.'))

    @api.constrains('email')
    def _check_email(self):
        """Basic email validation"""
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError(_('Please enter a valid email address.'))
