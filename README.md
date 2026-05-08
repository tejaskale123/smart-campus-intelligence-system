# Smart Campus Intelligence System

A Django-based campus management system with role-based dashboards for admins, teachers, and students. The project includes student management, teacher management, attendance marking, attendance records, analytics pages, reports, and responsive dashboard UI.

## Features

- Role-based login for admin, teacher, and student users
- Admin dashboard with student, teacher, attendance, analytics, reports, and settings links
- Teacher dashboard with student list and attendance tools
- Student dashboard with attendance, performance, and profile pages
- Teacher management: add, edit, delete, and list teachers
- Student management backed by MongoDB student records
- Attendance system backed by Django SQLite models
- Professional attendance add/list pages with Present/Absent badges
- Responsive sidebar layout and dashboard styling

## Tech Stack

- Python
- Django 5.2
- SQLite for Django users, roles, sessions, and attendance records
- MongoDB with PyMongo for student records used by the student management module
- HTML, CSS, JavaScript
- Font Awesome icons

## Project Structure

```text
smart-campus-intelligence-system/
|-- backend/
|   |-- apps/
|   |   |-- authentication/
|   |   |-- attendance/
|   |   |-- students/
|   |   |-- teachers/
|   |   |-- analytics/
|   |   |-- canteen/
|   |   |-- devices/
|   |   |-- library/
|   |   |-- notifications/
|   |   |-- realtime/
|   |   `-- security/
|   |-- config/
|   |   |-- settings.py
|   |   `-- urls.py
|   |-- database/
|   |   `-- mongo.py
|   |-- static/
|   |-- templates/
|   |-- media/
|   |-- db.sqlite3
|   |-- manage.py
|   `-- requirements.txt
|-- docs/
|-- frontend/
`-- README.md
```

## Setup

### 1. Go to Backend

```powershell
cd backend
```

### 2. Create and Activate Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you are using the existing conda environment on this machine:

```powershell
C:\Users\admin\miniconda3\envs\campus_env\python.exe manage.py runserver
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Start Server

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Sample Users

These users are useful for local testing if present in `db.sqlite3`:

| Role | Username | Password |
| --- | --- | --- |
| Teacher | `teacher1` | `teacher123` |
| Student | `student1` | `student123` |
| Student | `student2` | `student123` |
| Student | `student3` | `student123` |

To create or repair the sample teacher/student users:

```powershell
python manage.py shell
```

```python
from django.contrib.auth.models import User

users = [
    ("teacher1", "teacher123", "teacher1@gmail.com", "teacher"),
    ("student1", "student123", "student1@gmail.com", "student"),
    ("student2", "student123", "student2@gmail.com", "student"),
    ("student3", "student123", "student3@gmail.com", "student"),
]

for username, password, email, role in users:
    user, _ = User.objects.get_or_create(username=username, defaults={"email": email})
    user.email = email
    user.set_password(password)
    user.save()
    user.userprofile.role = role
    user.userprofile.save()
```

## Attendance Flow

1. Login as teacher:

```text
teacher1 / teacher123
```

2. Open Add Attendance:

```text
http://127.0.0.1:8000/add-attendance/
```

3. Select a student from the dropdown:

```text
student1 - student1@gmail.com
student2 - student2@gmail.com
student3 - student3@gmail.com
```

4. Select status:

```text
Present
Absent
```

5. Save attendance.

6. Open attendance records:

```text
http://127.0.0.1:8000/attendance-list/
```

The attendance record is saved in the Django SQLite database using `apps.attendance.models.Attendance`.

## Important Routes

| Route | Purpose |
| --- | --- |
| `/` | Login page |
| `/login/` | Login page |
| `/logout/` | Logout |
| `/register/` | Register |
| `/dashboard/` | Role-based dashboard redirect |
| `/admin-dashboard/` | Admin dashboard |
| `/teacher-dashboard/` | Teacher dashboard |
| `/student-dashboard/` | Student dashboard |
| `/students/` | Student list |
| `/add-student/` | Add student |
| `/teachers/` | Teacher list |
| `/add-teacher/` | Add teacher |
| `/add-attendance/` | Add attendance |
| `/attendance-list/` | Attendance records |
| `/analytics/` | Analytics |
| `/reports/` | Reports |
| `/settings/` | Settings |

## Databases

The project currently uses both SQLite and MongoDB:

- SQLite stores Django auth users, `UserProfile`, sessions, teachers, and attendance records.
- MongoDB stores student-management records used by the students module.

MongoDB connection file:

```text
backend/database/mongo.py
```

Default MongoDB URL:

```text
mongodb://localhost:27017/
```

## Common Commands

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Using the existing `campus_env`:

```powershell
C:\Users\admin\miniconda3\envs\campus_env\python.exe manage.py check
C:\Users\admin\miniconda3\envs\campus_env\python.exe manage.py migrate
C:\Users\admin\miniconda3\envs\campus_env\python.exe manage.py runserver
```

## Troubleshooting

### Student Dropdown Is Empty

Create users with `userprofile.role = "student"`:

```python
from django.contrib.auth.models import User

user = User.objects.create_user(
    username="student1",
    password="student123",
    email="student1@gmail.com",
)
user.userprofile.role = "student"
user.userprofile.save()
```

### Attendance Is Not Showing

Check that records exist:

```powershell
python manage.py shell
```

```python
from apps.attendance.models import Attendance
Attendance.objects.count()
```

### MongoDB Error

Make sure MongoDB is running locally before using MongoDB-backed student features.

### Login Redirects Unexpectedly

Check the user's role:

```python
from django.contrib.auth.models import User
user = User.objects.get(username="teacher1")
user.userprofile.role
```

## Notes

- Keep `SECRET_KEY`, email passwords, and other secrets out of production code.
- Use environment variables for production settings.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS` before deployment.
- Do not commit local database files, virtual environments, cache files, or media uploads in production repositories.
