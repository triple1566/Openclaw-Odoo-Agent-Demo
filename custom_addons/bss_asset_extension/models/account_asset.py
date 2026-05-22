from odoo import models, fields, api
from datetime import timedelta

class Account_Asset(models.Model):
    _inherit = "account.asset"
    #depreciation = 감가상각
    #default depreciation date set to today + 7
    depreciation_date = fields.Date(required=True, default=(fields.Date.today() + timedelta(days=7)))
    depreciation_countdown = fields.Integer(compute = '_compute_depreciation_countdown', readonly=True, store = True)
    #! set readonly for depreciation flag count to True later
    depreciation_flag_count = fields.Integer(readonly=False,default=0)
    alerted = fields.Boolean(default=False, readonly=True)
    #parent linkage to the child field of account.analytic.account
    branch_name = fields.Many2one('account.analytic.account')
    transfer_state = fields.Selection(
        selection=[('none', 'No Transfer'), ('transferred', 'Transferred')],
        string="Transfer Status",
        default='none',
        tracking=True,
        readonly=True
    )
    transfer_log_ids = fields.One2many(
        comodel_name='bss.asset.transfer.log',
        inverse_name='asset_id',
        string='Transfer History',
        readonly=True,
    )
    transfer_count = fields.Integer(default=0, string='Transfer Count')
    last_transfer_date = fields.Date(compute='_compute_last_transfer_date', string='Last Transfer Date',store=True)
    #Residual value goes into journal-debit(interbranch transfer account)
    residual_value=fields.Float(compute='_compute_residual_value', readonly=True)
    #accumulated depreciation goes into journal-cumulative depreciation
    accumulated_depreciation = fields.Float(compute = "_compute_accumulated_depreciation", readonly=True, default=0)
    #gross valur (original value) goes into journal-credit(asset account)


    #compute days left til depreciation date
    @api.depends('depreciation_date')
    def _compute_depreciation_countdown(self):
        today = fields.Date.today(self)
        for rec in self:
            if not rec.depreciation_date:
                continue
            diff = (rec.depreciation_date-today).days
            rec.depreciation_countdown = diff if diff >= 0 else -1

    #compute depreciation accumulation:
    def _compute_accumulated_depreciation(self):
        for rec in self:
            #! value 100 should be later replaced by the user's depreciation expense amount
            rec.accumulated_depreciation = rec.depreciation_flag_count*100

    #compute residual value: 
    @api.depends('book_value', 'accumulated_depreciation')
    def _compute_residual_value(self):
        for rec in self:
            val = rec.book_value - rec.accumulated_depreciation
            rec.residual_value = val if val>=0 else 0

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

        need_depreciation = self.search([
            ('depreciation_countdown', '==', 0)
        ])

        for rec in need_depreciation:
            rec.depreciation_flag_count+=1

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
                'default_from_branch': self.branch_name.id,
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

    def set_to_running(self):
        for asset in self:
            broken_moves = asset.depreciation_move_ids.filtered(lambda move: not move.asset_depreciation_beginning_date)
            for move in broken_moves:
                move.asset_depreciation_beginning_date = move.date or asset.prorata_date or fields.Date.today()
        return super().set_to_running()