from odoo import models


class product_template(models.Model):
    _inherit = 'product.product'

    def _action_open_apply_tag_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Apply Tag',
            'res_model': 'bss.tag.behaviour.apply.tag.wizard',
            'view_mode': 'form',
            'views': [(self.env.ref('bss_tag_behaviour.view_bss_apply_tag_wizard_form').id, 'form')],
            'target': 'new',
            'context': {
                'default_active_model': self._name,
                'active_model': self._name,
                'active_ids': self.ids,
            },
        }