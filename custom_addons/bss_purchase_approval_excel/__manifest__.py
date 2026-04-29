{
    "name": "BSS Purchase Approval & Product Excel",
    "version": "1.0",
    "summary": "Purchase approval workflow and product Excel import/export",
    "category": "Purchases",
    "author": "BSS",
    "license": "LGPL-3",
    "depends": ["base", "purchase", "product"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "data/cron_data.xml",
        "views/purchase_approval_configuration_views.xml",
        "views/purchase_order_views.xml",
        "views/product_template_views.xml",
        "views/product_excel_wizard_views.xml",
        "views/menu_views.xml"
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "sequence":1
}
