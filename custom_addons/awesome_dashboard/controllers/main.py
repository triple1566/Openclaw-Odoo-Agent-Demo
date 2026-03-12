from odoo import http
from odoo.http import request


class AwesomeDashboardController(http.Controller):

    @http.route('/awesome_dashboard/statistics', type='json', auth='user')
    def statistics(self):
        """Return dashboard statistics for the awesome_dashboard page.
        In a real production module these figures would come from ORM queries;
        here we return illustrative demo values so the tutorial works out of
        the box without a custom t-shirt order model.
        """
        return {
            'new_orders_count': 36,
            'new_orders_amount': 12450.75,
            'average_quantity': 4.2,
            'cancelled_orders': 5,
            'average_time': 3.4,          # days from 'new' to 'sent'/'cancelled'
            'orders_by_size': {
                'S': 22,
                'M': 48,
                'L': 35,
                'XL': 18,
                'XXL': 7,
            },
        }
