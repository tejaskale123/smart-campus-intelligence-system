from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Attendance

from apps.authentication.models import UserProfile


@login_required
def attendance_list(request):

    attendance_records = Attendance.objects.all().order_by('-id')

    context = {

        'attendance_records': attendance_records

    }

    return render(

        request,

        'attendance/attendance_list.html',

        context
    )


@login_required
def add_attendance(request):

    students = User.objects.filter(

        userprofile__role='student'
    )

    if request.method == 'POST':

        student_id = request.POST.get('student')

        status = request.POST.get('status')

        if student_id and status:

            student = User.objects.get(id=student_id)

            Attendance.objects.create(

                student=student,

                status=status
            )

            return redirect('attendance_list')

    context = {

        'students': students

    }

    return render(

        request,

        'attendance/add_attendance.html',

        context
    )
