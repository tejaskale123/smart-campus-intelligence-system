from django.urls import path

from .views import (

    login_page,
    dashboard,

    add_student,
    students_list,

    update_student,
    delete_student,

    add_attendance,
    attendance_list,

    student_detail,

    register_page,

    logout_page

)


urlpatterns = [

    # ==========================
    # LOGIN (ROOT)
    # ==========================

    path(
        '',
        login_page,
        name='login'
    ),


    # ==========================
    # LOGIN
    # ==========================

    path(
        'login/',
        login_page,
        name='login'
    ),


    # ==========================
    # DASHBOARD
    # ==========================

    path(
        'dashboard/',
        dashboard,
        name='dashboard'
    ),


    # ==========================
    # ADD STUDENT
    # ==========================

    path(
        'add-student/',
        add_student,
        name='add_student'
    ),


    # ==========================
    # STUDENTS LIST
    # ==========================

    path(
        'students/',
        students_list,
        name='students_list'
    ),


    # ==========================
    # UPDATE STUDENT
    # ==========================

    path(
        'update-student/<str:student_id>/',
        update_student,
        name='update_student'
    ),


    # ==========================
    # DELETE STUDENT
    # ==========================

    path(
        'delete-student/<str:student_id>/',
        delete_student,
        name='delete_student'
    ),


    # ==========================
    # ADD ATTENDANCE
    # ==========================

    path(
        'add-attendance/',
        add_attendance,
        name='add_attendance'
    ),


    # ==========================
    # ATTENDANCE LIST
    # ==========================

    path(
        'attendance-list/',
        attendance_list,
        name='attendance_list'
    ),
# ==========================
# STUDENT DETAIL
# ==========================

path(
    'student/<str:student_id>/',
    student_detail,
    name='student_detail'
),


# ==========================
# LOGOUT
# ==========================

path(
    'logout/',
    logout_page,
    name='logout'
),

# ==========================
# REGISTER
# ==========================

path(
    'register/',
    register_page,
    name='register'
),

]

