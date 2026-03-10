# Student Customize Module - (bss_student)

The Student Customize Module manages Students, Classes, Subjects, and Attendance, and integrates with res.partner to automatically create and synchronize student contact records.

## Models & Fields Student (bss.student)

* name (Char, required) - Student full name
* student_number (Char, read-only) - Auto-generated sequence STD/0001
* dob (Date) ? age (Integer, computed)
* roll_number (Char, unique)
* gender (Selection: Male/Female/Other)
* email, phone
* photo (Binary)
* class_id (Many2one ? bss.class)
* subject_ids (Many2many ? auto-filled from class)
* attendance_ids (One2many ? bss.attendance)

## Logic

* Auto-create/update related res.partner on student create/write
* Auto-fill subjects when class selected
* Age computed from DOB

## Class (bss.class)

* name (Char, required)
* code (Char, required, unique)
* subject_ids (Many2many ? bss.subject)
* Display format: Name (Code) in dropdowns
* Unique constraint on class.code
* Display class as Name (Code)

## Subject (bss.subject)

* name (Char, required)

## Attendance (bss.attendance)

* attendance_number (Char, read-only) - Sequence ATD/YYYY/MONTH/0001
* student_id (Many2one ? bss.student)
* status (Selection: Present/Absent/Leave)
* checkin_time, checkout_time

## Partner (res.partner) Extension

* is_student (Boolean)
* student_id (Many2one ? bss.student)
* Auto-sync name, email, phone from student
* How to link partner as a login Student Management student user.

## Sequences

* Student Number: STD/0001 ? auto on create
* Attendance Number: ATD/YYYY/MONTH/0001 ? auto on create

## Functional Logic

* Auto-create/update partner on student create/write
* Auto-fill subjects when class chosen
* Age calculated from DOB
* Roll number & class code validations
* Display class as Name (Code)

## User Security (bss_student_access_right)

To implement user security for the student module. First, please create new custom module 'bss_student_access_right' and inherit the existing student module. And then add two user roles with different access levels:

* Student User:
o View only their own student profile & attendance
o Cannot create/edit/delete
o Cannot access class or subject data
o Link user to partner
* Student Admin:
o Full CRUD on students, attendance, classes, subjects
o Full module management
