from odoo import api, fields, models
from odoo.fields import Domain


class AccountReport(models.Model):
    _inherit = 'account.report'

    expense_category_ids = fields.Many2many('bss.expense.category', string='Expense Categories')

    def _is_general_ledger_report(self):
        self.ensure_one()
        general_ledger = self.env.ref('account_reports.general_ledger_report', raise_if_not_found=False)
        return bool(general_ledger) and self.id == general_ledger.id

    def _init_options_expense_category_ids(self, options, previous_options):
        if not self._is_general_ledger_report():
            return
        options['expense_category_ids'] = previous_options.get('expense_category_ids', self.expense_category_ids.ids)

    @api.model
    def _get_options_expense_category_domain(self, options):
        selected_ids = [int(category_id) for category_id in options.get('expense_category_ids', [])]
        if not selected_ids:
            return Domain.TRUE
        return Domain('expense_category', 'in', selected_ids)

    def _get_options_domain(self, options, date_scope):
        domain = super()._get_options_domain(options, date_scope)
        if not self._is_general_ledger_report():
            return domain
        return Domain.AND([domain, self._get_options_expense_category_domain(options)])