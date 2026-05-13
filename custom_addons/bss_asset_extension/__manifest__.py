{
    "name": "BSS Asset Extension",
    "version": "1.0",
    "summary": "Scaffold module for asset-related extensions",
    "category": "Custom",
    "author": "BSS",
    "license": "LGPL-3",
    "depends": ["base","mail","account_asset", "product", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/account_asset_cron.xml",
        "data/low_stock_cron.xml",
        "views/account_asset_list_view.xml",
        "views/product_low_stock_views.xml",
        "views/menu_views.xml",
        "wizard/asset_transfer_wizard_views.xml",
        "views/account_asset_transfer_views.xml",
        "report/asset_summary_report.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "sequence": 1
}
