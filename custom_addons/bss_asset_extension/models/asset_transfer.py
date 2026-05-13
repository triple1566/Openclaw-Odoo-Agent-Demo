from odoo import fields, models


class BssAssetTransferLog(models.Model):
    _name = 'bss.asset.transfer.log'
    _description = 'Asset Branch Transfer Log'
    _order = 'transfer_date desc, id desc'

    asset_id = fields.Many2one('account.asset', required=True, ondelete='cascade')
    from_branch = fields.Char(string='From Branch')
    to_branch = fields.Char(string='To Branch', required=True)
    transfer_date = fields.Date(default=fields.Date.context_today, required=True)
    user_id = fields.Many2one('res.users', string='Transferred By', default=lambda self: self.env.user, required=True)
    note = fields.Text()