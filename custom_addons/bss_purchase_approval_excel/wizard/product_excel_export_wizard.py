from odoo import _, fields, models
from odoo.exceptions import UserError


class ProductExcelExportWizard(models.TransientModel):
    _name = "product.excel.export.wizard"
    _description = "Product Excel Export Wizard"

    include_archived = fields.Boolean(string="Include Archived Products")

    def action_export_products(self):
        self.ensure_one()
        raise UserError(_("Product Excel export logic is not implemented yet."))
