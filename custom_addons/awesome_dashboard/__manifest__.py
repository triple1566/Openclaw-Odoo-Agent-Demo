# -*- coding: utf-8 -*-
{
    'name': "Awesome Dashboard",

    'summary': """
        Odoo JS Framework Tutorial — Chapter 2: Build a Dashboard
    """,

    'description': """
        Implements all 11 exercises from the "Build a dashboard" chapter of
        the Odoo JavaScript framework tutorial:

        1.  Layout component with control panel
        2.  Customers / Leads quick-navigation buttons
        3.  Generic DashboardItem card with configurable size
        4.  RPC call to /awesome_dashboard/statistics
        5.  Statistics service with memoized caching
        6.  Pie chart via lazy-loaded Chart.js
        7.  Reactive statistics that auto-refresh every 10 minutes
        8.  Lazy-loaded dashboard bundle (LazyComponent)
        9.  Generic NumberCard / PieChartCard components
        10. Extensible item registry (awesome_dashboard category)
        11. Settings dialog to show/hide items (persisted in localStorage)
    """,

    'author': "BSS",
    'website': "https://www.odoo.com",

    'category': 'Tutorials/AwesomeDashboard',
    'version': '1.0',

    # crm is needed for the Leads button (crm.lead model).
    # Remove it from depends if crm is not installed in your database.
    'depends': ['base', 'web', 'crm'],

    'application': True,
    'installable': True,

    'data': [
        'views/actions.xml',
    ],

    'assets': {
        # Always-loaded: the lazy-loader stub + the statistics service.
        # The service must be in web.assets_backend so Odoo starts it at app
        # boot.  Components that call useService() can only find services that
        # were started during app initialisation.
        'web.assets_backend': [
            'awesome_dashboard/static/src/dashboard_action.js',
            'awesome_dashboard/static/src/dashboard/statistics_service.js',
        ],
        # Lazy-loaded bundle (exercise 8): every dashboard file EXCEPT
        # statistics_service.js, which lives in web.assets_backend above.
        # We list files explicitly so the service is never included twice
        # (duplicate module definitions crash the JS module loader).
        'awesome_dashboard.dashboard_assets': [
            'awesome_dashboard/static/src/dashboard/dashboard.scss',
            'awesome_dashboard/static/src/dashboard/dashboard_item.js',
            'awesome_dashboard/static/src/dashboard/dashboard_item.xml',
            'awesome_dashboard/static/src/dashboard/number_card.js',
            'awesome_dashboard/static/src/dashboard/number_card.xml',
            'awesome_dashboard/static/src/dashboard/pie_chart.js',
            'awesome_dashboard/static/src/dashboard/pie_chart.xml',
            'awesome_dashboard/static/src/dashboard/pie_chart_card.js',
            'awesome_dashboard/static/src/dashboard/pie_chart_card.xml',
            'awesome_dashboard/static/src/dashboard/configuration_dialog.js',
            'awesome_dashboard/static/src/dashboard/configuration_dialog.xml',
            'awesome_dashboard/static/src/dashboard/dashboard_items.js',
            'awesome_dashboard/static/src/dashboard/dashboard.js',
            'awesome_dashboard/static/src/dashboard/dashboard.xml',
        ],
    },

    'license': 'AGPL-3',
}
