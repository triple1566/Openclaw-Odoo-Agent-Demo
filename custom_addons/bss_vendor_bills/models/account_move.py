from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    expense_category = fields.Many2one('bss.expense.category', string='Expense Category')

    def _post(self, soft=True):
        val = super()._post(soft)
        for rec in self:
            if rec.expense_category:
                rec.line_ids.write({'expense_category': rec.expense_category.id})
        return val