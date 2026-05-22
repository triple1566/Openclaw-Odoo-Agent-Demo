from odoo import fields, models
from odoo.exceptions import UserError


class BssAssetTransferWizard(models.TransientModel):
    _name = 'bss.asset.transfer.wizard'
    _description = 'Asset Branch Transfer Wizard'

    asset_id = fields.Many2one('account.asset', required=True, readonly=True)
    from_branch = fields.Many2one('account.analytic.account', related='asset_id.branch_name', readonly=True)
    to_branch = fields.Many2one('account.analytic.account')
    transfer_date = fields.Date(default=fields.Date.context_today, required=True)
    note = fields.Text()

    def action_confirm_transfer(self):
        self.ensure_one()
        if self.from_branch and self.from_branch.id == self.to_branch.id:
            raise UserError('The destination branch must be different from the current branch.')

        #store name, id before modification of original asset
        name=self.asset_id.name
        prev_id = self.asset_id.id

        self.asset_id.write({
            'transfer_state': 'transferred',
            'state': "close",
            'name': f'{name} V{self.asset_id.transfer_count}'
        })
        #copies previous asset record's data to a dummy variable
        vals = self.asset_id.copy_data()[0]
        vals.pop('message_follower_ids', None)
        vals.pop('message_partner_ids', None)
        vals.pop('activity_ids', None)

        vals.update({
            'transfer_count': self.asset_id.transfer_count+1,
            'branch_name': self.to_branch.id,
            'state': 'open',
            'active': True,
            'name': name,
            'last_transfer_date': self.transfer_date
        })
        #create new asset with dummy variable
        transferred_asset = self.env['account.asset'].create(vals)
        
        self.env['bss.asset.transfer.log'].create({
            'asset_id': self.asset_id.id,
            'from_branch': self.from_branch,
            'to_branch': self.to_branch,
            'transfer_date': self.transfer_date,
            'note': self.note,
        })

        #search for all previously owned transfer logs
        prev_log = self.env['bss.asset.transfer.log'].search([
            ('asset_id','==',prev_id)
        ])
        #point all prev logs to currently held asset
        for log in prev_log:
            log.asset_id = transferred_asset.id

        #! use this if you need to reference current branch
        #branch = self.env['account.analytic.account'].search([('id','==',self.to_branch.id)])

        #ping transfer noti
        self.asset_id.message_post(
            body=f"Asset transferred from {self.from_branch.name or 'N/A'} to {self.to_branch.name} on {self.transfer_date}."
        )

        prev_msg = self.env['mail.message'].search([
            ('res_id','==',prev_id)
        ])
        for msg in prev_msg:
            msg.res_id = transferred_asset.id

        #! Implement debit/credit requirements!

        return {'type': 'ir.actions.act_window_close'}