{
    'name': 'BSS Student Access Right',
    'version': '1.0.0',
    'category': 'Education',
    'summary': 'Role-based security for BSS Student Management',
    'author': 'BSS',
    'depends': ['bss_student'],
    'data': [
        'security/student_security.xml',
        'security/ir.model.access.csv',
        'security/student_record_rules.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
