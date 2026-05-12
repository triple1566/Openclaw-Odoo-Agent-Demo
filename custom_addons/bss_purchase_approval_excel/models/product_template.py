import base64
from io import BytesIO

from odoo import _, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    uom_po_id = fields.Many2one(
        'uom.uom',
        string='Purchase UoM',
        help="Default unit of measure used for purchase orders. It must be in the same category as the default unit of measure."
    )

    def action_import_product_template(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Import Products (Excel)",
            "res_model": "product.excel.import.wizard",
            "view_mode": "form",
            "target": "new",
        }

    def _export_cell_value(self, value):
        return value or ""

    def action_export_product_template(self):
        try:
            import xlsxwriter
        except Exception as exc:
            raise UserError(_("xlsxwriter is required to export products to Excel.")) from exc

        products = self.env["product.template"].with_context(active_test=False).search([], order="id")
        output = BytesIO()
        workbook = None
        try:
            workbook = xlsxwriter.Workbook(output, {"in_memory": True})
            sheet = workbook.add_worksheet("Products")

            header_format = workbook.add_format({"bold": True, "bg_color": "#D9E1F2"})

            headers = [
                "Name",
                "Product Type",
                "Product Code",
                "Unit of Measure",
                "Purchase UoM",
            ]

            for col, title in enumerate(headers):
                sheet.write(0, col, title, header_format)
                sheet.set_column(col, col, 24)

            for row, product in enumerate(products, start=1):
                sheet.write(row, 0, self._export_cell_value(product.name))
                sheet.write(row, 1, self._export_cell_value(product.type))
                sheet.write(row, 2, self._export_cell_value(product.default_code))
                sheet.write(row, 3, self._export_cell_value(product.uom_id.display_name))
                # Export purchase UoM if set, otherwise use default UoM
                purchase_uom = product.uom_po_id if product.uom_po_id else product.uom_id
                sheet.write(row, 4, self._export_cell_value(purchase_uom.display_name))

            notes = workbook.add_worksheet("Notes")
            notes.set_column(0, 0, 100)
            note_lines = [
                "This export contains all product templates currently available in the system.",
                "Product Type values follow Odoo's product.template type field.",
                "Product Code is exported from the Internal Reference field (default_code).",
                "Unit of Measure and Purchase UoM are exported using their display names.",
                "Purchase UoM defaults to the standard Unit of Measure if not explicitly set.",
            ]
            for row, line in enumerate(note_lines):
                notes.write(row, 0, line)

        finally:
            if workbook:
                workbook.close()

        file_content = base64.b64encode(output.getvalue())
        attachment = self.env["ir.attachment"].create(
            {
                "name": "product_export.xlsx",
                "type": "binary",
                "datas": file_content,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "res_model": "product.template",
                "res_id": False,
            }
        )

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }
