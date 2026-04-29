from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RankConfiguration(models.Model):
    _name = "rank.configuration"
    _description = "Rank Configuration"
    _order = "rank_code, id"

    rank_name = fields.Char(required=True)
    rank_code = fields.Integer(required=True)
    status = fields.Selection(
        [("active", "Active"), ("deactive", "Inactive")],
        required=True,
        default="active",
    )
    default_rank = fields.Boolean(default=False)
    discount_percentage = fields.Float(required=True, default=0.0)
    threshold_line_ids = fields.One2many(
        "rank.configuration.line", "rank_id", string="Sales Thresholds"
    )

    _sql_constraints = [
        ("rank_code_unique", "unique(rank_code)", "Rank Code must be unique."),
    ]

    @api.constrains("discount_percentage")
    def _check_discount_percentage(self):
        for rec in self:
            if rec.discount_percentage < 0.0 or rec.discount_percentage > 100.0:
                raise ValidationError(_("Discount Percentage must be between 0 and 100."))

    @api.constrains("default_rank")
    def _check_one_default_rank(self):
        for rec in self.filtered("default_rank"):
            default_count = self.search_count(
                [("default_rank", "=", True), ("id", "!=", rec.id)]
            )
            if default_count:
                raise ValidationError(
                    _("Only one rank can be set as Default at a time.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._normalize_default_rank()
        return records

    def write(self, vals):
        result = super().write(vals)
        self._normalize_default_rank()
        return result

    def _normalize_default_rank(self):
        default_ranks = self.search([("default_rank", "=", True)], order="id desc")
        if len(default_ranks) > 1:
            default_ranks[1:].write({"default_rank": False})

    @api.model
    def _get_rank_for_total_sales(self, total_amount):
        line = self.env["rank.configuration.line"].search(
            [
                ("rank_id.status", "=", "active"),
                ("from_amount", "<=", total_amount),
                "|",
                ("to_amount", "=", 0.0),
                ("to_amount", ">=", total_amount),
            ],
            order="from_amount desc, id desc",
            limit=1,
        )
        if line:
            return line.rank_id

        return self.search(
            [("default_rank", "=", True), ("status", "=", "active")],
            limit=1,
        )

    @api.model
    def _cron_update_customer_rank(self):
        partners = self.env["res.partner"].search([("customer_rank", ">", 0)])
        if not partners:
            return

        grouped_sales = self.env["sale.order"].read_group(
            [
                ("state", "in", ["sale", "done"]),
                ("partner_id", "in", partners.ids),
            ],
            ["partner_id", "amount_total:sum"],
            ["partner_id"],
            lazy=False,
        )

        totals_by_partner = {
            item["partner_id"][0]: item.get("amount_total", 0.0) for item in grouped_sales
        }

        for partner in partners:
            total = totals_by_partner.get(partner.id, 0.0)
            rank = self._get_rank_for_total_sales(total)
            partner.rank_code = rank.id if rank else False


class RankConfigurationLine(models.Model):
    _name = "rank.configuration.line"
    _description = "Rank Threshold Line"
    _order = "from_amount, id"

    rank_id = fields.Many2one("rank.configuration", required=True, ondelete="cascade")
    from_amount = fields.Float(required=True, default=0.0)
    to_amount = fields.Float(default=0.0, help="Use 0 for no upper limit.")

    @api.constrains("from_amount", "to_amount")
    def _check_amounts(self):
        for rec in self:
            if rec.from_amount < 0.0:
                raise ValidationError(_("From Amount cannot be negative."))
            if rec.to_amount and rec.to_amount < rec.from_amount:
                raise ValidationError(
                    _("To Amount must be greater than or equal to From Amount.")
                )

    @api.constrains("rank_id", "from_amount", "to_amount")
    def _check_range_overlap(self):
        for rec in self:
            siblings = self.search(
                [("rank_id", "=", rec.rank_id.id), ("id", "!=", rec.id)]
            )
            for sibling in siblings:
                rec_to = rec.to_amount if rec.to_amount else float("inf")
                sibling_to = sibling.to_amount if sibling.to_amount else float("inf")
                overlap = rec.from_amount <= sibling_to and sibling.from_amount <= rec_to
                if overlap:
                    raise ValidationError(
                        _("Threshold ranges in the same rank cannot overlap.")
                    )
