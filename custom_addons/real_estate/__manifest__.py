{
    'name':'Real Estate',
    'version':'1.0',
    'sequence': 1,
    'author':'Leo Jeong',
    'summary':'Leos Odoo Real Estate',
    'category':'tools',
    'images': ['static/description/icon.png'],
    'depends':['base', 'mail'],
    'data':[
        "security/ir.model.access.csv",
        "data/estate_property_cron.xml",
        "report/estate_property_report.xml",
        "views/estate_property_views.xml",
        "views/estate_property_wizard_views.xml",
        "views/res_users_views.xml",
        "views/real_estate_menu.xml",
    ],
    'application':True
}