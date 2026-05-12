from odoo import _, fields, models
from odoo.exceptions import UserError


class ProductTagApplyWizard(models.TransientModel):
    _name = 'bss.tag.behaviour.apply.tag.wizard'
    _description = 'Apply Tags to Product Records'

    active_model = fields.Char(readonly=True)
    tag_ids = fields.Many2many(
        'product.tag',
        string='Tags',
        required=True,
        help='Selected tags will be applied to the records opened from the current action.',
    )

    def action_apply_tags(self):
        self.ensure_one()
        active_model = self.env.context.get('active_model') or self.active_model
        active_ids = self.env.context.get('active_ids') or []
        if not active_model or not active_ids:
            raise UserError(_('Please select at least one product record before applying tags.'))

        records = self.env[active_model].browse(active_ids).exists()
        if not records:
            raise UserError(_('The selected records are no longer available.'))

        if active_model == 'product.template':
            records.write({'product_tag_ids': [(4, tag.id) for tag in self.tag_ids]})
        elif active_model == 'product.product':
            records.write({'additional_product_tag_ids': [(4, tag.id) for tag in self.tag_ids]})
        else:
            raise UserError(_('Apply Tag is only available for product templates and product variants.'))

        return {'type': 'ir.actions.act_window_close'}