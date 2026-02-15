from odoo import models, fields, api

class ClawChat(models.Model):
    _name="claw.chat"
    _description="Openclaw Chat"
    
    llm_model = fields.Char(required=True, default="GPT-4o-mini")