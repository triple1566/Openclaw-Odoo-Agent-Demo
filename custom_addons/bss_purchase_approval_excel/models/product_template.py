import base64
from io import BytesIO

from odoo import _, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_export_product_template(self):
        try:
            import xlsxwriter
        except Exception as exc:
            raise UserError(_("xlsxwriter is required to export the Excel template.")) from exc

        output = BytesIO()
        workbook = None
        try:
            workbook = xlsxwriter.Workbook(output, {"in_memory": True})
            sheet = workbook.add_worksheet("Product Template")

            header_format = workbook.add_format({"bold": True, "bg_color": "#D9E1F2"})
            required_format = workbook.add_format({"bg_color": "#FFF2CC"})

            headers = [
                "Name*",
                "Internal Reference",
                "Product Type*",
                "Category",
                "Sales Price",
                "Cost",
                "Unit of Measure*",
                "Purchase UoM*",
                "Can be Sold",
                "Can be Purchased",
            ]
            sample = [
                "Sample Product",
                "SKU-001",
                "consu",
                "All",
                100.0,
                60.0,
                "Units",
                "Units",
                True,
                True,
            ]

            for col, title in enumerate(headers):
                sheet.write(0, col, title, header_format)
                sheet.set_column(col, col, 20)

            for col, value in enumerate(sample):
                if headers[col].endswith("*"):
                    sheet.write(1, col, value, required_format)
                else:
                    sheet.write(1, col, value)

            notes = workbook.add_worksheet("Notes")
            notes.set_column(0, 0, 100)
            note_lines = [
                "Columns marked with * are required to create a product.",
                "Allowed Product Type values: consu, service, combo.",
                "Category must match an existing Product Category name.",
                "Unit of Measure and Purchase UoM must match existing UoM names.",
            ]
            for row, line in enumerate(note_lines):
                notes.write(row, 0, line)

        finally:
            if workbook:
                workbook.close()

        file_content = base64.b64encode(output.getvalue())
        attachment_res_id = self[:1].id if len(self) == 1 else False
        attachment = self.env["ir.attachment"].create(
            {
                "name": "product_create_template.xlsx",
                "type": "binary",
                "datas": file_content,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "res_model": "product.template",
                "res_id": attachment_res_id,
            }
        )

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }
