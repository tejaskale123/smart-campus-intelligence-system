# 🎓 Smart Campus Intelligence System

<div align="center">

![Smart Campus ERP](https://img.shields.io/badge/Smart_Campus-ERP_System-0066ff?style=for-the-badge&logo=graduation-cap&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2.14-092E20?style=for-the-badge&logo=django&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4.17.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)

**A professional, enterprise-grade Smart Campus ERP Dashboard built with Django + MongoDB**

*Clean UI • Secure Authentication • Real-time Analytics • Attendance Tracking*

</div>

---

## 📌 Overview

**Smart Campus Intelligence System** is a full-stack, production-ready **Enterprise Resource Planning (ERP)** web application designed specifically for educational institutions. It provides a centralized platform for managing students, tracking attendance, and visualizing campus analytics — all within a sleek, modern **dark glassmorphic SaaS dashboard UI**.

The system follows a **strict role-based access flow**:
- 🔐 Unauthenticated users land directly on the **Login Page** (no sidebar)
- ✅ After successful login, the **full ERP Dashboard with sidebar** is unlocked
- 🔒 All private routes are protected using Django's `@login_required` decorator

---

## ✨ Features

### 🔐 Authentication System
- Secure **Login Page** with username & password
- **Password show/hide** toggle
- **Remember Me** checkbox
- Loading spinner button on form submit
- Django CSRF token protection on all forms
- **Register** new admin accounts
- **Logout** with redirect back to Login

### 📊 Admin Dashboard
- Live **analytics cards**: Total Students, Total Attendance, Present, Absent
- **Monthly Attendance Bar Chart** (Chart.js)
- **Present vs Absent Doughnut Chart** (Chart.js)
- All data fetched live from MongoDB

### 👨‍🎓 Student Management
- **Add Student** with profile image upload
- **Students List** with search functionality
- **Attendance percentage** displayed per student
- **Low Attendance Alert** badge (below 75%)
- **Update** and **Delete** student records
- **Student Detail Profile** page with full attendance history

### 📅 Attendance Tracking
- **Add Attendance** record (Student Name, Date, Present/Absent)
- **Attendance List** with search by student name
- **Total Present / Total Absent** summary cards
- Color-coded **Present** (green) and **Absent** (red) status badges

---

## 🏗️ Project Architecture

```
smart-campus-intelligence-system/
│
├── backend/                        # Main Django project root
│   ├── apps/
│   │   └── authentication/         # Core app (views, urls, services)
│   │       ├── views.py            # All view functions
│   │       ├── urls.py             # URL routing
│   │       ├── services.py         # DB service layer
│   │       └── decorators.py       # @admin_only decorator
│   │
│   ├── config/
│   │   ├── settings.py             # Django project settings
│   │   └── urls.py                 # Root URL configuration
│   │
│   ├── database/
│   │   └── mongo.py                # MongoDB connection (PyMongo)
│   │
│   ├── templates/
│   │   ├── base/
│   │   │   ├── base.html           # ERP layout (WITH sidebar)
│   │   │   └── auth_base.html      # Auth layout (NO sidebar)
│   │   ├── authentication/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── dashboard/
│   │   │   └── admin_dashboard.html
│   │   ├── students/
│   │   │   ├── students_list.html
│   │   │   ├── add_student.html
│   │   │   ├── update_student.html
│   │   │   └── student_detail.html
│   │   └── attendance/
│   │       ├── add_attendance.html
│   │       └── attendance_list.html
│   │
│   ├── static/
│   │   └── css/
│   │       └── style.css           # Global design system (CSS Variables, Glassmorphism)
│   │
│   ├── media/                      # Student profile images
│   ├── manage.py
│   └── requirements.txt
│
└── README.md
```

---

## 🛣️ URL Routes

| URL | View | Access |
|-----|------|--------|
| `/` | Login Page | Public |
| `/login/` | Login Page | Public |
| `/register/` | Register Page | Public |
| `/logout/` | Logout | Private |
| `/dashboard/` | Admin Dashboard | 🔒 Login Required |
| `/add-student/` | Add Student Form | 🔒 Login Required |
| `/students/` | Students List | 🔒 Login Required |
| `/update-student/<id>/` | Edit Student | 🔒 Login Required |
| `/delete-student/<id>/` | Delete Student | 🔒 Login Required |
| `/student/<id>/` | Student Profile | 🔒 Login Required |
| `/add-attendance/` | Add Attendance | 🔒 Login Required |
| `/attendance-list/` | Attendance List | 🔒 Login Required |

---

## 🔐 Application Flow

```
Open Website (/)
      ↓
 Login Page  ← No Sidebar, Clean Auth UI
      ↓
  Authenticate
      ↓
   Dashboard  ← Full ERP Sidebar Visible
      ↓
Students / Attendance / Analytics
      ↓
    Logout
      ↓
 Back to Login
```

---

## 🎨 UI Design System

The frontend uses a **Dark Futuristic SaaS ERP** design language built entirely with **Vanilla CSS + CSS Variables**. No frameworks like Tailwind or Bootstrap are used.

### Design Tokens (CSS Variables)
```css
--bg-primary:       #020817   /* Main background     */
--bg-secondary:     #0f172a   /* Card background     */
--neon-blue:        #0066ff   /* Primary accent      */
--neon-cyan:        #00f3ff   /* Secondary accent    */
--success:          #00ff88   /* Present / Good      */
--danger:           #ff0055   /* Absent / Low        */
--text-primary:     #e2e8f0   /* Main text           */
--text-secondary:   #94a3b8   /* Muted text          */
```

### UI Components
- **Glassmorphism Cards** — `backdrop-filter: blur` + `rgba` backgrounds
- **Professional Tables** — Sticky headers, hover row effects, status badges
- **Responsive Grid** — CSS Grid with `auto-fit` / `minmax` layouts
- **Collapsible Sidebar** — Mobile-friendly hamburger menu
- **Animated Buttons** — Gradient fill, hover lift, loading spinner states

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Framework** | Django 5.2.14 |
| **Database** | MongoDB (PyMongo 4.17.0) |
| **REST API** | Django REST Framework 3.17.1 |
| **WebSockets** | Django Channels 4.3.2 |
| **Authentication** | Django Auth + JWT (PyJWT 2.12.1) |
| **Computer Vision** | OpenCV + face-recognition + dlib |
| **Data Processing** | NumPy, Pandas, Pillow |
| **Charts** | Chart.js (CDN) |
| **Icons** | Font Awesome 6.5.1 (CDN) |
| **Fonts** | Google Fonts — Poppins, Inter |
| **Frontend** | Vanilla HTML, CSS, JavaScript |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- MongoDB (running locally or Atlas URI)
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/smart-campus-intelligence-system.git
cd smart-campus-intelligence-system
```

### 2. Create Virtual Environment
```bash
python -m venv campus_env

# Windows
campus_env\Scripts\activate

# macOS/Linux
source campus_env/bin/activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure MongoDB
Open `backend/database/mongo.py` and set your MongoDB connection string:
```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["smart_campus_db"]
```

### 5. Configure Django Settings
In `backend/config/settings.py`, ensure your `SECRET_KEY` and `ALLOWED_HOSTS` are set:
```python
SECRET_KEY = 'your-secret-key-here'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
```

### 6. Run Database Migrations
```bash
python manage.py migrate
```

### 7. Create a Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 8. Run the Development Server
```bash
python manage.py runserver
```

### 9. Open in Browser
```
http://127.0.0.1:8000/
```
You will be redirected to the **Login Page** automatically.

---

## 📸 Pages Overview

| Page | Description |
|------|-------------|
| **Login** | Centered glassmorphic auth card, no sidebar, password toggle |
| **Register** | Create new admin account |
| **Dashboard** | Live analytics cards + Chart.js charts |
| **Students List** | Searchable table with attendance %, status badges |
| **Add Student** | Form with profile image upload |
| **Student Profile** | Detailed profile with attendance history |
| **Add Attendance** | Quick attendance record entry |
| **Attendance List** | Full searchable attendance log with badges |

---

## 🗃️ MongoDB Collections

| Collection | Fields |
|-----------|--------|
| `students` | `name`, `course`, `age`, `email`, `profile_image` |
| `attendance_logs` | `student_name`, `attendance_date`, `status` |

---

## 🔒 Security Features

- ✅ Django CSRF Protection on all forms
- ✅ `@login_required` on all private routes
- ✅ `@admin_only` decorator for admin-level access
- ✅ Password hashing via Django's auth system
- ✅ Auth pages have **no sidebar** (sidebar injection prevention)
- ✅ Session-based authentication

---

## 📱 Responsive Design

The entire application is **fully responsive** across all device sizes:

| Screen | Layout |
|--------|--------|
| Desktop (1200px+) | Full sidebar + multi-column grid |
| Tablet (768px–992px) | Collapsible sidebar via hamburger |
| Mobile (<768px) | Single column, full-width forms & tables |

---

## 📧 Low Attendance Alert System

When a student's attendance drops **below 75%**, the system:
1. Displays a **"Low Attendance"** warning badge in the student list
2. Automatically triggers an **email alert** to the student's registered email address

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use it for educational and commercial purposes.

---

## 👨‍💻 Author

**Smart Campus Intelligence System**
Built with ❤️ using Django + MongoDB

---

<div align="center">

⭐ **Star this repo if you found it useful!** ⭐

</div>
