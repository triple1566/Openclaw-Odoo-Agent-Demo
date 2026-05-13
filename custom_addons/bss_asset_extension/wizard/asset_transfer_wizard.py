from odoo import fields, models
from odoo.exceptions import UserError


class BssAssetTransferWizard(models.TransientModel):
    _name = 'bss.asset.transfer.wizard'
    _description = 'Asset Branch Transfer Wizard'

    asset_id = fields.Many2one('account.asset', required=True, readonly=True)
    from_branch = fields.Char(readonly=True)
    to_branch = fields.Char(required=True)
    transfer_date = fields.Date(default=fields.Date.context_today, required=True)
    note = fields.Text()

    def action_confirm_transfer(self):
        self.ensure_one()
        if self.from_branch and self.from_branch.strip() == self.to_branch.strip():
            raise UserError('The destination branch must be different from the current branch.')

        self.env['bss.asset.transfer.log'].create({
            'asset_id': self.asset_id.id,
            'from_branch': self.from_branch,
            'to_branch': self.to_branch,
            'transfer_date': self.transfer_date,
            'note': self.note,
        })
        self.asset_id.write({
            'branch_name': self.to_branch,
            'transfer_state': 'transferred',
        })
        self.asset_id.message_post(
            body=f"Asset transferred from {self.from_branch or 'N/A'} to {self.to_branch} on {self.transfer_date}."
        )
        return {'type': 'ir.actions.act_window_close'}