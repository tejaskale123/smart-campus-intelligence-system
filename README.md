# Smart Campus Intelligence System

A Django-based campus management system for role-based dashboards, student and teacher management, attendance tracking, analytics, reporting, and AI-assisted face attendance.

The project uses SQLite for Django authentication, sessions, and role profiles, while MongoDB stores operational campus data such as students, users mirror records, attendance logs, face data, analytics, and system logs.

## Features

- Role-based login for admin, teacher, and student users
- Admin dashboard for students, teachers, analytics, reports, and settings
- Teacher dashboard with student lists and attendance tools
- Student dashboard with profile, attendance, and performance views
- Student records stored in MongoDB
- Teacher accounts managed through Django auth and mirrored in MongoDB
- Public registration saved in Django SQLite and MongoDB `users`
- Manual attendance marking with present/absent status
- Attendance history and searchable attendance records
- Browser/webcam face registration
- Face attendance with OpenCV, `face_recognition`, dlib, and MongoDB
- Face encodings saved in `face_encodings` and first encoding mirrored in `face_data`
- Login, security, notification, camera, and attendance session logs
- CSV and PDF report export
- Responsive Django-template UI

## Tech Stack

**Backend**

- Python
- Django 5.2.14
- Django REST Framework
- Django Channels
- SQLite
- MongoDB
- PyMongo

**AI and Image Processing**

- face-recognition
- dlib
- OpenCV
- NumPy
- Pillow

**Frontend**

- Django templates
- HTML
- CSS
- JavaScript
- Font Awesome

## Project Structure

```text
smart-campus-intelligence-system/
|-- backend/
|   |-- ai_engine/
|   |-- api/
|   |-- apps/
|   |   |-- authentication/        # Auth, roles, dashboards, students, reports, face features
|   |   |-- attendance/            # Attendance app routes
|   |   |-- students/              # Student dashboard pages
|   |   |-- teachers/              # Teacher app shell
|   |   `-- analytics/             # Analytics app shell
|   |-- components/
|   |-- config/                    # Django settings, root URLs, ASGI, WSGI
|   |-- database/
|   |   `-- mongo.py               # MongoDB connection
|   |-- media/                     # Uploaded/generated media
|   |-- services/
|   |-- static/                    # CSS and static assets
|   |-- templates/                 # Django templates
|   |-- utils/
|   |-- db.sqlite3                 # Local SQLite database
|   |-- manage.py
|   `-- requirements.txt
|-- docs/
|-- frontend/
`-- README.md
```

## Requirements

- Python 3.10 or newer recommended
- MongoDB running locally on `localhost:27017`
- Webcam for face registration and face attendance
- Visual C++ build tools on Windows if `dlib` needs to compile from source

## Installation

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

Open the app:

```text
http://127.0.0.1:8000/
```

If `python` is not available in PATH, use the Python launcher or your virtual environment executable:

```powershell
py manage.py runserver
.\venv\Scripts\python.exe manage.py runserver
```

## MongoDB Setup

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

Important collections:

| Collection | Purpose |
| --- | --- |
| `users` | Mongo mirror for newly registered Django users |
| `students` | Student records and face registration student data |
| `teachers` | Teacher records mirrored from Django users |
| `attendance_logs` | Manual and face attendance records |
| `face_data` | Simplified face record with student name, id, and first encoding |
| `face_encodings` | Full face encoding/sample records used by face matching |
| `login_logs` | Successful login logs |
| `security_logs` | Failed login and security events |
| `camera_logs` | Face camera events |
| `notification_logs` | Attendance notification logs |
| `attendance_sessions` | Attendance session records |
| `analytics_cache` | Cached analytics snapshots |
| `ai_predictions` | AI/analytics prediction logs |

## SQLite and MongoDB Responsibilities

| Database | Used For |
| --- | --- |
| SQLite | Django auth users, passwords, sessions, migrations, `UserProfile` roles |
| MongoDB | Students, users mirror, teachers mirror, attendance, logs, analytics, face data |

Both databases are used together. Do not delete `db.sqlite3` unless you are ready to recreate Django users and roles.

## User Registration Flow

New public registrations go through:

```text
backend/apps/authentication/views/auth_views.py
```

When a user registers:

1. Django creates the main auth user in SQLite.
2. `UserProfile` is created automatically through the post-save signal.
3. MongoDB receives a mirror document in `users`.
4. The terminal prints:

```text
USER SAVED IN MONGO
```

Example MongoDB `users` document:

```json
{
  "_id": "ObjectId(...)",
  "username": "tejas",
  "email": "tejas@gmail.com",
  "role": "student",
  "user_id": "1",
  "created_at": "..."
}
```

The current register page only asks for username and password. If email or role fields are not posted, email is saved as an empty string and role defaults to `student`.

## User Roles

Roles are stored in `apps.authentication.models.UserProfile`:

- `admin`
- `teacher`
- `student`

Superusers are automatically assigned the `admin` role. Normal registered users default to `student`.

Update a role in Django shell:

```powershell
cd backend
python manage.py shell
```

```python
from django.contrib.auth.models import User

user = User.objects.get(username="teacher1")
user.userprofile.role = "teacher"
user.userprofile.save()
```

## Key Routes

| Route | Purpose |
| --- | --- |
| `/` | Login page |
| `/login/` | Login page |
| `/logout/` | Logout |
| `/register/` | Public user registration |
| `/dashboard/` | Role-based dashboard redirect |
| `/admin-dashboard/` | Admin dashboard |
| `/teacher-dashboard/` | Teacher dashboard |
| `/student-dashboard/` | Student dashboard |
| `/students/` | Student list |
| `/students-list/` | Legacy student list route |
| `/add-student/` | Add student |
| `/update-student/<student_id>/` | Update student |
| `/delete-student/<student_id>/` | Delete student |
| `/student/<student_id>/` | Student detail |
| `/teachers/` | Teacher list |
| `/add-teacher/` | Add teacher |
| `/update-teacher/<teacher_id>/` | Update teacher |
| `/delete-teacher/<teacher_id>/` | Delete teacher |
| `/add-attendance/` | Manual attendance |
| `/attendance-list/` | Attendance records |
| `/attendance-history/` | Attendance history |
| `/my-attendance/` | Student attendance page |
| `/performance/` | Student performance page |
| `/my-profile/` | Student profile page |
| `/register-face/` | Face registration |
| `/face-attendance/` | Face attendance page |
| `/start-face-attendance/` | Start OpenCV face attendance |
| `/process-face-attendance/` | Process browser camera face attendance |
| `/analytics/` | Analytics dashboard |
| `/reports/` | Reports page |
| `/performance-report/` | Performance report |
| `/download-pdf-report/` | Download PDF report |
| `/export-csv-report/` | Export CSV report |
| `/settings/` | Admin settings |
| `/admin/` | Django admin |

## Face Registration Flow

Face registration is handled in:

```text
backend/apps/authentication/views/face_views.py
```

Flow:

1. Open `/register-face/`.
2. Enter student details.
3. Allow camera permission.
4. Capture 5 images.
5. Backend extracts face samples and encodings.
6. Student data is saved in MongoDB `students`.
7. Full face documents are saved in `face_encodings`.
8. First face encoding is saved in `face_data`.
9. Terminal prints:

```text
CAMERA START
[0.12, 0.44, ...]
FACE SAVED SUCCESS
```

Example MongoDB `face_data` document:

```json
{
  "_id": "ObjectId(...)",
  "student_name": "Tejas",
  "student_id": "1",
  "roll_number": "101",
  "course": "BCA",
  "face_encoding": [0.12, 0.44, 0.88],
  "created_at": "..."
}
```

## Face Attendance Flow

Flow:

1. Open `/face-attendance/`.
2. Start camera attendance.
3. App loads known faces from MongoDB.
4. Captured face is compared against stored encodings/samples.
5. Matching student is marked in `attendance_logs`.
6. First valid detection marks check-in, later valid detection can mark check-out.

Face matching reads from `face_encodings` and `students`, so both collections should be kept.

## Manual Attendance Flow

Flow:

1. Login as admin or teacher.
2. Open `/add-attendance/`.
3. Select a student.
4. Choose date and status.
5. Save attendance.
6. Record is inserted into MongoDB `attendance_logs`.

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

### `python` command not found

Use:

```powershell
py manage.py runserver
.\venv\Scripts\python.exe manage.py runserver
```

### MongoDB collection shows `0 of 0`

This means MongoDB is connected, but no insert has run for that collection yet.

For new user registration, register a new user and check terminal:

```text
USER SAVED IN MONGO
```

Then refresh MongoDB Compass collection:

```text
smart_campus_db -> users -> Refresh
```

For face registration, register a new face and check terminal:

```text
FACE SAVED SUCCESS
```

Then refresh:

```text
smart_campus_db -> face_data -> Refresh
```

### Face encoding is not generated

If terminal does not show an encoding array, the face was not detected clearly.

Try:

- Better lighting
- One face only in the camera frame
- Face centered and not too close
- Camera permission enabled
- Clean webcam lens

### `face_recognition` or `dlib` install fails

On Windows, install Visual C++ build tools or use a Python version with available wheels. You can also install dependencies inside a clean virtual environment.

### Login redirects to the wrong dashboard

Check the user's role:

```python
from django.contrib.auth.models import User

user = User.objects.get(username="tejas")
print(user.userprofile.role)
```

Update it:

```python
user.userprofile.role = "student"
user.userprofile.save()
```

### Student does not appear in attendance dropdown

Check MongoDB `students`. A student should have at least one usable name field:

- `name`
- `student_name`
- `full_name`

Useful optional fields:

- `roll_number`
- `course`
- `department`
- `email`
- `student_email`

### Static files or images are missing

During development, keep `DEBUG=True`. Static and media paths are:

```text
backend/static/
backend/media/
```

## Development Notes

- Keep `SECRET_KEY`, email credentials, and production database settings out of committed code.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS` before deployment.
- Do not commit virtual environments, cache files, `__pycache__`, generated media, or local database dumps.
- Keep SQLite and MongoDB in sync when adding new user or student workflows.
- Face recognition accuracy depends heavily on lighting, camera quality, and image angle.
- MongoDB Compass may need manual Refresh after inserts.

## Current Status

Core dashboards, authentication, role profiles, student management, teacher management, manual attendance, face registration, face attendance, analytics, reports, and MongoDB logging are implemented for local development and academic/project use.
