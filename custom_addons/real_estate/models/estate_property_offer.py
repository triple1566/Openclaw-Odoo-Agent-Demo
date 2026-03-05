from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class estate_property_offer(models.Model):
    _name = "estate.property.offer"
    _description = "estate property offer"
    _order = "price desc"

    @api.model_create_multi
    def create(self, vals_list):
        property_model = self.env["estate.property"]
        for vals in vals_list:
            property_id = vals.get("property_id")
            new_price = vals.get("price")
            if not property_id or new_price is None:
                continue

            property_record = property_model.browse(property_id)
            existing_prices = property_record.offer_ids.mapped("price")
            if existing_prices:
                highest_price = max(existing_prices)
                if float_compare(new_price, highest_price, precision_digits=2) < 0:
                    raise UserError("The offer price must be higher than or equal to existing offers.")

        offers = super().create(vals_list)
        offers.mapped("property_id").filtered(lambda p: p.state == "new").write({"state": "offer_received"})
        return offers

    @api.constrains('price')
    def _check_price_positive(self):
        for record in self:
            if float_compare(record.price, 0, precision_digits=2) <= 0:
                raise ValidationError(
                    "Offer price must be strictly positive."
                )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            base_date = fields.Date.to_date(record.create_date) or fields.Date.today()
            record.date_deadline = fields.Date.add(base_date, days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                base_date = fields.Date.to_date(record.create_date) or fields.Date.today()
                deadline = fields.Date.to_date(record.date_deadline) or fields.Date.today()
                record.validity = (deadline - base_date).days

    def accept_offer(self):
        if self.property_id.offer_ids.filtered(lambda o: o.status == 'accepted'):
            raise UserError("Only one offer can be accepted per property.")
        self.status = 'accepted'
        self.property_id.write({
            'selling_price': self.price,
            'buyer': self.partner_id.id,
        })

    def refuse_offer(self):
        self.status = 'refused'

    price = fields.Float()
    status = fields.Selection(
        [
            ("new", "New"),
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        default="new",
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")