from odoo import models, fields, api
from datetime import timedelta

class Account_Asset(models.Model):
    _inherit = "account.asset"
    #depreciation = 감가상각

    #default depreciation date set to today + 7
    depreciation_date = fields.Date(required=True, default=(fields.Date.today() + timedelta(days=7)))
    depreciation_countdown = fields.Integer(compute = '_compute_depreciation_countdown', readonly=True, store = True)
    alerted = fields.Boolean(default=False, readonly=True)
    branch_name = fields.Char(string="Current Branch", tracking=True)
    transfer_state = fields.Selection(
        selection=[('none', 'No Transfer'), ('transferred', 'Transferred')],
        string="Transfer Status",
        default='none',
        tracking=True,
    )
    transfer_log_ids = fields.One2many(
        comodel_name='bss.asset.transfer.log',
        inverse_name='asset_id',
        string='Transfer History',
        readonly=True,
    )
    transfer_count = fields.Integer(compute='_compute_transfer_count', string='Transfer Count')
    last_transfer_date = fields.Date(compute='_compute_last_transfer_date', string='Last Transfer Date')

    #compute days left til depreciation date
    @api.depends('depreciation_date')
    def _compute_depreciation_countdown(self):
        today = fields.Date.today(self)
        for rec in self:
            if not rec.depreciation_date:
                continue
            diff = (rec.depreciation_date-today).days
            rec.depreciation_countdown = diff if diff >= 0 else 0

    @api.depends('transfer_log_ids')
    def _compute_transfer_count(self):
        for rec in self:
            rec.transfer_count = len(rec.transfer_log_ids)

    @api.depends('transfer_log_ids.transfer_date')
    def _compute_last_transfer_date(self):
        for rec in self:
            dates = rec.transfer_log_ids.mapped('transfer_date')
            rec.last_transfer_date = max(dates) if dates else False

    # Cron job for depreciation alert
    def _depreciation_alert(self):
        need_alert = self.search([
            ('depreciation_countdown', '<=', 7),
            ('alerted', '=', False)
        ])

        if not len(need_alert):
            print("stopping loop. no need for alerts.")
            return

        for rec in need_alert:
            rec.message_post(body=f"Your asset {rec.name} is nearing its depreciation date!")
            rec.alerted = True

    def action_open_transfer_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transfer Asset',
            'res_model': 'bss.asset.transfer.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_asset_id': self.id,
                'default_from_branch': self.branch_name,
            },
        }

    def action_view_transfer_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transfer History',
            'res_model': 'bss.asset.transfer.log',
            'view_mode': 'tree,form',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id},
        }