from odoo import fields, models


class BssExpenseCategory(models.Model):
    _name = 'bss.expense.category'
    _description = 'Expense Category'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
