from odoo import models, fields, api
from datetime import timedelta

class Account_Asset(models.Model):
    _inherit = "account.asset"
    #depreciation = 감가상각

    #default depreciation date set to today + 7
    depreciation_date = fields.Date(required=True, default=(fields.Date.today() + timedelta(days=7)))
    depreciation_countdown = fields.Integer(compute = '_compute_depreciation_countdown', readonly=True)
    alerted = fields.Boolean(default=False, readonly=True)

    #compute days left til depreciation date
    @api.depends('depreciation_date')
    def _compute_depreciation_countdown(self):
        today = fields.Date.today(self)
        for rec in self:
            if not rec.depreciation_date:
                continue
            diff = rec.depreciation_date-today
            rec.depreciation_countdown = diff.days
        return

    # Cron job for depreciation alert
    def _depreciation_alert(self):
        need_alert = self.search([
            ('depreciation_countdown', '<=', 7),
            ('alerted', '=', False)
        ])

        for rec in need_alert:
            if rec.message_post(body = f"Your asset {rec.name} is nearing its depreciation date!"):
                rec.alerted = True

        return