{
    "name": "BSS Vendor Bills",
    "version": "1.0",
    "summary": "Vendor bill custom module skeleton",
    "category": "Accounting",
    "author": "BSS",
    "license": "LGPL-3",
    "depends": ["base", "account", "account_reports"],
    "data": [
        "security/ir.model.access.csv",
        "data/expense_category_data.xml",
        "views/expense_category_views.xml",
        "views/account_report_views.xml",
        "views/account_move_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bss_vendor_bills/static/src/xml/expense_category_filter.xml",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "sequence": 1
}
