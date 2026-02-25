from odoo import models, fields, api

class ClawChat(models.Model):
    _name="claw.chat"
    _description="Openclaw Chat Sessions"
    
    creator = fields.Char(required=True, default="user")
    llm_model = fields.Char(required=True, default="GPT-4o-mini")
    hook_token = fields.Char(required=True, default="DEFAULT_TOKEN")
    tailnet_addr = fields.Char(required=True, default="http://mytailnet.com")
