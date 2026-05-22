from odoo import fields, models, api

class account_analytic_account(models.Model):
    _inherit="account.analytic.account"

    branch_of = fields.Many2one(comodel_name="account.asset",string="Branch Of",required=False,ondelete="set null",index=True,help="Branch associated with this analytic account",)