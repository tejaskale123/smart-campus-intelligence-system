from django.urls import path
from . import views

urlpatterns = [

    path(
        'add-attendance/',
        views.add_attendance,
        name='add_attendance'
    ),

    path(
        'attendance-list/',
        views.attendance_list,
        name='attendance_list'
    ),

]