import logging

from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


_logger = logging.getLogger(__name__)

class estate_property(models.Model):
    _name="estate.property"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="estate property"
    _order = "id desc"

    @api.ondelete(at_uninstall=False)
    def _unlink_except_new_or_cancelled(self):
        for record in self:
            if record.state not in ("new", "cancelled"):
                raise UserError("Only new or cancelled properties can be deleted.")

    @api.constrains('expected_price')
    def _check_expected_price_positive(self):
        for record in self:
            if float_compare(record.expected_price, 0, precision_digits=2) <= 0:
                raise ValidationError(
                    "Expected price must be strictly positive."
                )

    @api.constrains('selling_price')
    def _check_selling_price_positive(self):
        for record in self:
            if float_compare(record.selling_price, 0, precision_digits=2) < 0:
                raise ValidationError(
                    "Selling price must be positive."
                )

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price_percentage(self):
        for record in self:
            # Allow zero selling price (offer not yet accepted)
            if float_is_zero(record.selling_price, precision_digits=2):
                continue
            # Selling price must be at least 90% of expected price
            min_price = record.expected_price * 0.9
            if float_compare(record.selling_price, min_price, precision_digits=2) < 0:
                raise ValidationError(
                    f"The selling price cannot be lower than 90% of the expected price "
                    f"(expected: {record.expected_price}, minimum: {min_price})."
                )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("expected_price", "total_area")
    def _compute_price_per_sqm(self):
        for record in self:
            if record.total_area:
                record.price_per_sqm = record.expected_price / record.total_area
            else:
                record.price_per_sqm = 0.0

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.onchange("bedrooms")
    def _onchange_bedrooms_luxury(self):
        if self.bedrooms and self.bedrooms >= 5:
            self.description = "Luxury Mansion"

    def cancel(self):
        if self.state == 'sold':
            raise UserError("A sold property cannot be cancelled.")
        self.state = 'cancelled'

    def set_property_sold(self):
        if self.state == 'cancelled':
            raise UserError("A cancelled property cannot be sold.")
        self.state = 'sold'

    def set_property_new(self):
        for record in self:
            if record.state != 'cancelled':
                raise UserError("Only cancelled properties can be set back to new.")
            record.state = 'new'

    def action_open_sell_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Confirm Sale",
            "res_model": "estate.property.sell.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_property_id": self.id,
            },
        }

    @api.model
    def _cron_log_offer_received_count(self):
        count = self.search_count([("state", "=", "offer_received")])
        _logger.info("Offer Received properties count: %s", count)

    def write(self, vals):
        previous_prices = {record.id: record.expected_price for record in self}
        result = super().write(vals)
        if "expected_price" in vals:
            for record in self:
                old_price = previous_prices.get(record.id)
                if not old_price:
                    continue
                if float_compare(record.expected_price, old_price * 0.9, precision_digits=2) < 0:
                    message_post = getattr(record, "message_post", None)
                    if callable(message_post):
                        message_post(
                            body="Large price drop detected!",
                            message_type="comment",
                            subtype_xmlid="mail.mt_note",
                        )
        return result

    name=fields.Char(required=True)
    description=fields.Text()
    postcode=fields.Char()
    date_availability=fields.Date(default=fields.Date.add(fields.Date.today(), months=3),copy=False)
    expected_price=fields.Float(required=True)
    best_price=fields.Float(compute="_compute_best_price")
    price_per_sqm=fields.Float(compute="_compute_price_per_sqm")
    selling_price=fields.Float(copy=False)
    bedrooms=fields.Integer(default=2)
    living_area=fields.Integer()
    facades=fields.Integer()
    garage=fields.Boolean()
    garden=fields.Boolean()
    garden_area=fields.Integer()
    total_area=fields.Integer(compute="_compute_total_area")
    garden_orientation=fields.Selection(
        [
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        default='north',
        tracking=True
    )
    
    active=fields.Boolean(default=True)
    state=fields.Selection(
        [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        default='new',
        copy=False,
        required=True
    )
    property_type_id = fields.Many2one("estate.property.type")
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    buyer = fields.Many2one("res.partner")
    seller = fields.Many2one("res.partner")