{
    'name': 'Employee Asset Request',
    'version': '1.0.0',
    'category': 'Human Resources',
    'summary': 'Controlled request, approval, and assignment flow for company assets',
    'description': """
        Employee Asset Request Module
        =============================
        Structured and auditable process for requesting, approving,
        and assigning company assets such as laptops and phones.
    """,
    'author': 'BSS',
    'depends': ['base', 'hr', 'mail', 'account_asset'],
    'data': [
        'security/emp_asset_request_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/emp_asset_request_views.xml',
        'views/asset_assignment_wizard_views.xml',
        'views/account_asset_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
