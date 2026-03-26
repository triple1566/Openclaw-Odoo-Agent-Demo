{
    "name": "POS Order Source",
    "version": "1.0",
    "summary": "Add order source field to POS order",
    "author": "CK",
    "license": "LGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "views/pos_order_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_order_source/static/src/js/order_source_button.js",
            "pos_order_source/static/src/xml/control_buttons_inherit.xml",
            "pos_order_source/static/src/js/pos_order_patch.js",
            "pos_order_source/static/src/js/payment_screen_patch.js",
        ],
    },
    "installable": True,
    "application": False,
}