{
    'name':'Real Estate',
    'version':'1.0',
    'author':'Leo Jeong',
    'summary':'Leos Odoo Real Estate',
    'category':'tools',
    'depends':['base'],
    'data':[
        "security/ir.model.access.csv",
        "views/estate_property_views.xml",
        "views/real_estate_menu.xml",
    ],
    'application':True
}