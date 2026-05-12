{
    "name": "BSS Tag Behaviour",
    "version": "1.0",
    "summary": "tag behaviour alteration",
    "category": "Purchases",
    "author": "BSS",
    "license": "LGPL-3",
    "depends": ["base", "purchase", "product"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "views/product_tag_apply_wizard_views.xml",
        "views/product_list_tag_columns_views.xml",
        "views/menu_views.xml"
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "sequence":1
}
