{
    'name': 'BSS Student Management',
    'version': '1.0.0',
    'category': 'Education',
    'summary': 'Manage Students, Classes, Subjects, and Attendance',
    'description': """
        Student Management Module
        =========================
        Features:
        - Student registration with auto-generated student numbers
        - Class and subject management
        - Attendance tracking
        - Integration with res.partner
        - Auto-fill subjects from class
        - Age calculation from date of birth
    """,
    'author': 'BSS',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/bss_student_views.xml',
        'views/bss_class_views.xml',
        'views/bss_subject_views.xml',
        'views/bss_attendance_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 3
}
