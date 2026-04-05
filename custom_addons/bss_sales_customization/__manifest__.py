{
    "name": "BSS Sales Custom",
    "version": "1.0",
    "summary": "Customizations for Sales",
    "category": "Sales",
    "author": "BSS",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/rank_configuration_view.xml",
        "views/customer_rank_menu.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "sequence": 1,
}
