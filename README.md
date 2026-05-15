# Smart Campus Intelligence System

A Django-based campus management system for role-based dashboards, student and teacher management, attendance tracking, analytics, reporting, and AI-assisted face attendance.

The project combines Django auth and SQLite for application users with MongoDB for student records, attendance logs, face encodings, and reporting data.

## Features

- Role-based login for admin, teacher, and student users
- Admin dashboard with students, teachers, analytics, reports, and settings
- Teacher dashboard with student lists and attendance tools
- Student dashboard with personal attendance, profile, and performance pages
- Student management using MongoDB
- Teacher management using Django users and profiles
- Manual attendance marking with Present and Absent status
- Attendance history and searchable attendance records
- Face registration using webcam capture
- Face attendance using `face_recognition`, dlib, OpenCV, and MongoDB-stored face encodings
- Professional popup notifications using Django messages
- CSV and PDF report export
- Responsive sidebar-based UI

## Tech Stack

### Backend

- Python
- Django 5.2.14
- Django REST Framework
- Django Channels
- SQLite for Django auth, sessions, and relational app data
- MongoDB for students, attendance logs, face encodings, reports, and NoSQL records
- PyMongo

### AI and Image Processing

- face-recognition
- dlib
- OpenCV
- NumPy
- Pillow

### Frontend

- Django templates
- HTML
- CSS
- JavaScript
- Font Awesome

## Project Structure

```text
smart-campus-intelligence-system/
|-- backend/
|   |-- apps/
|   |   |-- authentication/        # Login, roles, dashboards, students, reports, face features
|   |   |-- attendance/            # Attendance model, form, URLs, legacy app views
|   |   |-- students/              # Student dashboard pages
|   |   |-- teachers/              # Teacher app shell
|   |   `-- analytics/             # Analytics app shell
|   |-- config/                    # Django settings, root URLs, ASGI, WSGI
|   |-- database/
|   |   `-- mongo.py               # MongoDB connection
|   |-- static/css/                # Application styles
|   |-- templates/                 # Django templates
|   |-- media/                     # Uploaded files and generated media
|   |-- db.sqlite3                 # Local SQLite database
|   |-- manage.py
|   `-- requirements.txt
|-- docs/
|-- frontend/
`-- README.md
```

## Prerequisites

- Python 3.10 or newer recommended
- MongoDB running locally on `localhost:27017`
- Webcam for face registration and face attendance
- Windows users may need Visual C++ build tools for `dlib` if installing from source

## Setup

From the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

If your machine uses the Python launcher or a named environment, replace `python` with the correct executable, for example:

```powershell
py manage.py runserver
```

## MongoDB

MongoDB is configured in:

```text
backend/database/mongo.py
```

Default connection:

```text
mongodb://localhost:27017/
```

Default database:

```text
smart_campus_db
```

Common collections used by the app:

- `students`
- `attendance_logs`
- `login_logs`
- `analytics_cache`
- `attendance_sessions`

Student face records should include a `face_encodings` field containing one or more 128-value face encoding arrays. Face registration also stores `face_samples` for fallback matching.

## User Roles

Roles are stored in `UserProfile`:

- `admin`
- `teacher`
- `student`

Create or update roles in the Django shell:

```powershell
python manage.py shell
```

```python
from django.contrib.auth.models import User

user = User.objects.create_user(
    username="teacher1",
    password="teacher123",
    email="teacher1@example.com",
)
user.userprofile.role = "teacher"
user.userprofile.save()
```

Superusers are automatically created with the `admin` role.

## Key Routes

| Route | Purpose | Access |
| --- | --- | --- |
| `/` | Login page | Public |
| `/login/` | Login | Public |
| `/logout/` | Logout | Authenticated |
| `/register/` | Access request / registration page | Public |
| `/dashboard/` | Role-based dashboard redirect | Authenticated |
| `/admin-dashboard/` | Admin dashboard | Admin |
| `/teacher-dashboard/` | Teacher dashboard | Teacher |
| `/student-dashboard/` | Student dashboard | Student |
| `/students/` | Student list | Admin / Teacher |
| `/add-student/` | Add student | Admin |
| `/student/<student_id>/` | Student detail | Authenticated, role guarded |
| `/teachers/` | Teacher list | Admin |
| `/add-teacher/` | Add teacher | Admin |
| `/add-attendance/` | Manual attendance | Admin / Teacher |
| `/attendance-list/` | Attendance records | Admin / Teacher |
| `/attendance-history/` | Attendance history | Authenticated |
| `/register-face/` | Face registration | Admin |
| `/face-attendance/` | Face attendance page | Authenticated |
| `/start-face-attendance/` | Start OpenCV camera attendance | Authenticated |
| `/process-face-attendance/` | Process browser camera frame | Authenticated |
| `/analytics/` | Analytics dashboard | Admin |
| `/reports/` | Reports page | Admin |
| `/download-pdf-report/` | Download PDF report | Admin |
| `/export-csv-report/` | Export CSV report | Admin |
| `/settings/` | Settings page | Admin |

## Face Registration Flow

1. Login as an admin.
2. Open `Register Face`.
3. Enter student name, roll number, and course.
4. Allow camera permission.
5. Capture 5 face samples.
6. The backend generates 128-value face encodings.
7. The student record is saved in MongoDB.

If encoding fails, the app returns an error instead of saving an empty `face_encodings` array. Keep the face centered, well lit, and visible inside the camera frame.

## Face Attendance Flow

1. Open `Face Attendance`.
2. Start the camera.
3. The app compares the live face with MongoDB `face_encodings`.
4. If matched, it marks attendance in `attendance_logs`.
5. First detection marks `IN`; second detection marks `OUT`.

## Manual Attendance Flow

1. Login as admin or teacher.
2. Open `Add Attendance`.
3. Select a student from the dropdown.
4. Choose the attendance date and status.
5. Save the record.

The dropdown reads students from MongoDB and supports records created through both normal student entry and face registration.

## Common Commands

```powershell
cd backend
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py test
```

## Troubleshooting

### Python command is not found

Use the Python launcher or your virtual environment path:

```powershell
py manage.py runserver
.\venv\Scripts\python.exe manage.py runserver
```

### MongoDB connection error

Make sure MongoDB is running locally:

```text
mongodb://localhost:27017/
```

Then verify `backend/database/mongo.py` still points to `smart_campus_db`.

### Face registration saves no encoding

Delete the bad student record with empty `face_encodings`, then register again with:

- Good lighting
- One face in the frame
- Face centered inside the scan box
- Camera permission enabled

The current backend blocks new records when face encoding fails.

### Student is not visible in attendance dropdown

Check the MongoDB `students` collection. The student should have at least one usable name field:

- `name`
- `student_name`
- `full_name`

The app also supports `course`, `department`, `student_course`, `email`, and `student_email` fallbacks.

### Login redirects to the wrong dashboard

Check the user's role:

```python
from django.contrib.auth.models import User

user = User.objects.get(username="teacher1")
user.userprofile.role
```

Update if needed:

```python
user.userprofile.role = "teacher"
user.userprofile.save()
```

### Static files or images are missing

During development, run the app with `DEBUG=True`. Uploaded files are served from:

```text
backend/media/
```

Static CSS files are in:

```text
backend/static/css/
```

## Development Notes

- Keep secrets out of committed code in production.
- Move `SECRET_KEY`, email credentials, and database settings to environment variables before deployment.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS` before production deployment.
- Do not commit local database files, virtual environments, cache files, generated media, or `__pycache__` files.
- Face recognition accuracy depends heavily on camera quality and lighting.

## Status

This is an active academic/project build. Core dashboards, role access, manual attendance, MongoDB-backed students, face registration, face attendance, reports, and notification UI are implemented.
