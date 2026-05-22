from odoo import fields, models
from odoo.exceptions import UserError


class BssAssetTransferWizard(models.TransientModel):
    _name = 'bss.asset.transfer.wizard'
    _description = 'Asset Branch Transfer Wizard'

    asset_id = fields.Many2one('account.asset', required=True, readonly=True)
    from_branch = fields.Many2one('account.analytic.account', related='asset_id.branch_name', readonly=True)
    to_branch = fields.Many2one('account.analytic.account')
    transfer_account_id = fields.Many2one(
        'account.account',
        string='Interbranch Transfer Account',
        required=True,
        domain="[('account_type', '!=', 'off_balance')]",
    )
    transfer_date = fields.Date(default=fields.Date.context_today, required=True)
    note = fields.Text()

    def action_confirm_transfer(self):
        self.ensure_one()
        if not self.to_branch:
            raise UserError('Please select a destination branch.')
        if self.from_branch and self.from_branch.id == self.to_branch.id:
            raise UserError('The destination branch must be different from the current branch.')

        source_asset = self.asset_id
        prev_id=source_asset.id
        original_name = source_asset.name
        source_asset._create_move_before_date(self.transfer_date)

        posted_depreciation = source_asset.depreciation_move_ids.filtered(
            lambda move: move.state == 'posted' and move.date <= self.transfer_date and move.depreciation_value
        )

        gross_value = source_asset.currency_id.round(abs(source_asset.original_value))
        residual_value = source_asset.currency_id.round(abs(source_asset.value_residual))
        depreciated_value = source_asset.currency_id.round(max(gross_value - residual_value, 0.0))

        if source_asset.currency_id.is_zero(residual_value):
            raise UserError('This asset has no residual value left to transfer.')

        source_distribution = source_asset.analytic_distribution or False
        destination_distribution = {str(self.to_branch.id): 100.0} if self.to_branch else False

        # 1) Source branch: close old asset and transfer residual value.
        source_move = self.env['account.move'].create({
            'date': self.transfer_date,
            'journal_id': source_asset.journal_id.id,
            'move_type': 'entry',
            'asset_depreciation_beginning_date': self.transfer_date,
            'ref': f'{source_asset.name} - Branch Transfer Out',
            'line_ids': [
                (0, 0, {
                    'name': f'{source_asset.name} - Transfer Out Asset',
                    'account_id': source_asset.account_asset_id.id,
                    'credit': gross_value,
                    'debit': 0.0,
                    'analytic_distribution': source_distribution,
                }),
                (0, 0, {
                    'name': f'{source_asset.name} - Transfer Out Accumulated Depreciation',
                    'account_id': source_asset.account_depreciation_id.id,
                    'debit': depreciated_value,
                    'credit': 0.0,
                    'analytic_distribution': source_distribution,
                }),
                (0, 0, {
                    'name': f'{source_asset.name} - Transfer Out Residual',
                    'account_id': self.transfer_account_id.id,
                    'debit': residual_value,
                    'credit': 0.0,
                    'analytic_distribution': source_distribution,
                }),
            ],
        })
        source_move.action_post()

        # 2) Destination branch: recognize asset at residual value.
        destination_move = self.env['account.move'].create({
            'date': self.transfer_date,
            'journal_id': source_asset.journal_id.id,
            'move_type': 'entry',
            'asset_depreciation_beginning_date': self.transfer_date,
            'ref': f'{source_asset.name} - Branch Transfer In',
            'line_ids': [
                (0, 0, {
                    'name': f'{source_asset.name} - Transfer In Asset',
                    'account_id': source_asset.account_asset_id.id,
                    'debit': residual_value,
                    'credit': 0.0,
                    'analytic_distribution': destination_distribution,
                }),
                (0, 0, {
                    'name': f'{source_asset.name} - Transfer In Clearing',
                    'account_id': self.transfer_account_id.id,
                    'credit': residual_value,
                    'debit': 0.0,
                    'analytic_distribution': destination_distribution,
                }),
            ],
        })
        destination_move.action_post()

        source_asset.write({
            'transfer_state': 'transferred',
            'state': "close",
            'name': f'{original_name} V{source_asset.transfer_count}',
        })

        vals = source_asset.copy_data()[0]
        vals.pop('message_follower_ids', None)
        vals.pop('message_partner_ids', None)
        vals.pop('activity_ids', None)
        vals.pop('depreciation_move_ids', None)
        vals.pop('original_move_line_ids', None)
        vals.pop('children_ids', None)
        vals.pop('parent_id', None)

        remaining_periods = max(source_asset.method_number - len(posted_depreciation), 1)
        vals.update({
            'original_value': residual_value,
            'salvage_value': 0.0,
            'already_depreciated_amount_import': 0.0,
            'transfer_count': source_asset.transfer_count + 1,
            'branch_name': self.to_branch.id,
            'state': 'draft',
            'active': True,
            'name': original_name,
            'last_transfer_date': self.transfer_date,
            'method_number': remaining_periods,
            'prorata_date': self.transfer_date,
            'acquisition_date': self.transfer_date,
            'analytic_distribution': destination_distribution,
        })

        transferred_asset = self.env['account.asset'].create(vals)
        transferred_asset.validate()

        self.env['bss.asset.transfer.log'].create({
            'asset_id': transferred_asset.id,
            'from_branch': self.from_branch.name if self.from_branch else False,
            'to_branch': self.to_branch.name,
            'transfer_date': self.transfer_date,
            'note': self.note,
        })

        source_asset.message_post(
            body=f"Asset transferred from {self.from_branch.name or 'N/A'} to {self.to_branch.name} on {self.transfer_date}."
        )

        prev_msg = self.env['mail.message'].search([
            ('res_id','==',prev_id)
        ])
        for msg in prev_msg:
            msg.res_id = transferred_asset.id

        return {'type': 'ir.actions.act_window_close'}