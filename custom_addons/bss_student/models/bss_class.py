# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BssClass(models.Model):
    _name = 'bss.class'
    _description = 'Class'

    name = fields.Char(string='Class Name', required=True)
    code = fields.Char(string='Class Code', required=True)
    subject_ids = fields.Many2many(
        'bss.subject',
        string='Subjects'
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Class code must be unique!')
    ]

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            if record.code and not record.code.strip():
                raise ValidationError(_('Class code cannot be empty or whitespace only.'))

    def name_get(self):
        """Display class as Name (Code)"""
        result = []
        for record in self:
            name = f"{record.name} ({record.code})"
            result.append((record.id, name))
        return result
