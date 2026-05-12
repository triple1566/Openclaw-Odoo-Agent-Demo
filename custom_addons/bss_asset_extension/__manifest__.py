{
    "name": "BSS Asset Extension",
    "version": "1.0",
    "summary": "Scaffold module for asset-related extensions",
    "category": "Custom",
    "author": "BSS",
    "license": "LGPL-3",
    "depends": ["base","mail","account_asset"],
    "data": [
        "security/ir.model.access.csv",
        "data/account_asset_cron.xml",
        "views/account_asset_list_view.xml",
        "views/menu_views.xml"
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "sequence": 1
}
