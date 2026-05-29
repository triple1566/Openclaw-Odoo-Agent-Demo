from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    expense_category = fields.Many2one('bss.expense.category', string='Expense Category')
    expense_category_name = fields.Char(related='expense_category.name', string='Expense Category Name', store=True, readonly=True)