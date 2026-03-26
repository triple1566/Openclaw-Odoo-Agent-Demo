# -*- coding: utf-8 -*-
{
    "name": "BSS POS Custom",
    "version": "19.0.1.0.0",
    "summary": "Custom POS configuration and order fields",
    "category": "Point of Sale",
    "author": "BSS",
    "license": "LGPL-3",
    "depends": ["base","point_of_sale"],
    "data": [
        "views/pos_config_views.xml",
        "views/pos_order_views.xml",
    ],
    'assets': {
    'point_of_sale._assets_pos': [
        'bss_pos_custom/static/src/js/patchposbutton.js',
        'bss_pos_custom/static/src/js/payment_validation_patch.js',
        'bss_pos_custom/static/src/xml/pos_button.xml',
    ],
},
    "installable": True,
    "application": False,
}
