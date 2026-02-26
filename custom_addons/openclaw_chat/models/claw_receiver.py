from odoo import models, fields

class claw_receiver(models.Model):
    _name="claw.receiver"
    _description="Openclaw's api call receiver"
    
    log = fields.Char()