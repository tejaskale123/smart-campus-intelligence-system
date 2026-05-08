# Smart Campus Intelligence System

A Django-based campus management project for role-based dashboards, student management, attendance tracking, analytics summaries, and low-attendance notifications.

## Project Overview

Smart Campus Intelligence System helps campus users manage students and attendance through separate dashboards for admins, teachers, and students.

- Admins can manage students, view dashboards, access reports, analytics, and settings pages.
- Teachers can view students, add attendance, and review attendance records.
- Students can view their own dashboard, attendance history, performance, and profile.
- Attendance and student data are stored in MongoDB.
- Django authentication and user roles are stored in SQLite.

## Tech Stack

- Python
- Django 5.2
- SQLite for Django auth and user profile data
- MongoDB with PyMongo for students and attendance records
- HTML, CSS, JavaScript
- Font Awesome icons
- Chart-ready dashboard scripts

## Main Features

- Login, logout, and registration
- Role-based access control
- Admin dashboard
- Teacher dashboard
- Student dashboard
- Student add, update, delete, list, search, and detail views
- Attendance add and attendance list views
- Student-specific attendance filtering
- Weekly and monthly attendance summaries
- Low attendance alert below 75%
- Email warning support for low attendance
- Responsive sidebar layout

## Project Structure

```text
smart-campus-intelligence-system/
|-- backend/
|   |-- apps/
|   |   |-- authentication/
|   |   |-- students/
|   |   |-- attendance/
|   |   |-- analytics/
|   |   |-- canteen/
|   |   |-- devices/
|   |   |-- library/
|   |   |-- notifications/
|   |   |-- realtime/
|   |   |-- security/
|   |   `-- teachers/
|   |-- config/
|   |   |-- settings.py
|   |   `-- urls.py
|   |-- database/
|   |   `-- mongo.py
|   |-- media/
|   |-- static/
|   |-- templates/
|   |-- db.sqlite3
|   |-- manage.py
|   `-- requirements.txt
|-- docs/
|-- frontend/
`-- README.md
```

## Prerequisites

Install these before running the project:

- Python 3.11 or newer
- MongoDB Community Server
- Git
- C++ build tools may be required for `dlib` and `face-recognition`

## Setup Instructions

### 1. Clone the Project

```bash
git clone <your-repository-url>
cd smart-campus-intelligence-system
```

### 2. Create and Activate Virtual Environment

Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
```

Linux or macOS:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `dlib` or `face-recognition` fails to install, install the required C++ build tools first, then run the command again.

### 4. Start MongoDB

Make sure MongoDB is running locally on:

```text
mongodb://localhost:27017/
```

The project uses this database:

```text
smart_campus_db
```

MongoDB collections used:

```text
students
attendance_logs
```

### 5. Run Django Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin User

```bash
python manage.py createsuperuser
```

Superusers automatically get the `admin` role through `UserProfile`.

### 7. Run Development Server

```bash
python manage.py runserver
```

Open the project in your browser:

```text
http://127.0.0.1:8000/
```

## User Roles

### Admin

Default access after creating a superuser.

Admin can access:

- `/admin-dashboard/`
- `/add-student/`
- `/students-list/`
- `/teachers/`
- `/analytics/`
- `/reports/`
- `/settings/`

### Teacher

Teacher users can access:

- `/teacher-dashboard/`
- `/add-attendance/`
- `/attendance-list/`
- `/students-list/`

To make a user a teacher, update the user role in Django admin or shell:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
user = User.objects.get(username="teacher_username")
user.userprofile.role = "teacher"
user.userprofile.save()
```

### Student

New registered users are assigned the `student` role by default.

Student users can access:

- `/student-dashboard/`
- `/student-profile/`
- `/attendance-list/`

For a student dashboard to show personal data, the Django username or email should match the MongoDB student record name or email.

## Important Routes

| Route | Purpose |
| --- | --- |
| `/` | Login page |
| `/login/` | Login page |
| `/register/` | Register page |
| `/logout/` | Logout |
| `/dashboard/` | Redirects user to role dashboard |
| `/admin-dashboard/` | Admin dashboard |
| `/teacher-dashboard/` | Teacher dashboard |
| `/student-dashboard/` | Student dashboard |
| `/add-student/` | Add student |
| `/students-list/` | Student list |
| `/student/<student_id>/` | Student detail |
| `/add-attendance/` | Add attendance |
| `/attendance-list/` | Attendance records |

## Email Configuration

Low-attendance warning emails use Gmail SMTP settings from:

```text
backend/config/settings.py
```

Update these values before using email alerts:

```python
EMAIL_HOST_USER = "yourgmail@gmail.com"
EMAIL_HOST_PASSWORD = "your_app_password"
```

Use a Gmail app password instead of your normal Gmail password.

## Database Notes

This project uses two databases:

- SQLite: Django users, sessions, admin, and `UserProfile`
- MongoDB: students and attendance logs

MongoDB connection file:

```text
backend/database/mongo.py
```

Current connection:

```python
client = MongoClient("mongodb://localhost:27017/")
db = client["smart_campus_db"]
```

## Static and Media Files

Static files:

```text
backend/static/
```

Templates:

```text
backend/templates/
```

Uploaded media files:

```text
backend/media/
```

During development, media files are served automatically when `DEBUG=True`.

## Common Commands

```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

## Troubleshooting

### MongoDB Connection Error

Check that MongoDB is installed and running on `localhost:27017`.

### Student Dashboard Shows No Profile

Make sure the logged-in user's username or email matches the student's `name` or `email` in MongoDB.

### Low Attendance Email Not Sending

Check Gmail SMTP settings and use an app password.

### Dependency Installation Fails

If `dlib` or `face-recognition` fails, install Visual Studio Build Tools on Windows or required compiler packages on Linux/macOS.

## Development Notes

- Keep secrets such as `SECRET_KEY` and email passwords out of production code.
- Set `DEBUG=False` before deployment.
- Configure `ALLOWED_HOSTS` before deployment.
- Use environment variables for production settings.
- Do not commit local database files, media uploads, virtual environments, or cache files in production repositories.

## Project Status

The current implementation includes the main Django authentication flow, role dashboards, MongoDB-backed student records, and attendance tracking. Some app folders such as library, canteen, realtime, security, devices, notifications, and analytics are present as future modules or placeholders.
