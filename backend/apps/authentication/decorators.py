from django.shortcuts import redirect
from django.http import HttpResponse

from .models import UserProfile


def get_user_role(user):
    if not user.is_authenticated:
        return None

    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return None


def redirect_by_role(user):
    role = get_user_role(user)

    if role == 'admin':
        return redirect('dashboard')

    if role == 'teacher':
        return redirect('teacher_dashboard')

    if role == 'student':
        return redirect('student_dashboard')

    return redirect('login')


# ==============================
# ADMIN ONLY
# ==============================

def admin_only(view_func):

    def wrapper(

        request,

        *args,

        **kwargs

    ):

        if request.user.userprofile.role == 'admin':

            return view_func(

                request,

                *args,

                **kwargs

            )

        return redirect_by_role(request.user)

    return wrapper


# ==============================
# TEACHER OR ADMIN
# ==============================

def teacher_or_admin(view_func):

    def wrapper(

        request,

        *args,

        **kwargs

    ):

        role = request.user.userprofile.role

        if role in [

            'admin',

            'teacher'

        ]:

            return view_func(

                request,

                *args,

                **kwargs

            )

        return redirect_by_role(request.user)

    return wrapper


# ==============================
# STUDENT ONLY
# ==============================

def student_only(view_func):

    def wrapper(

        request,

        *args,

        **kwargs

    ):

        if request.user.userprofile.role == 'student':

            return view_func(

                request,

                *args,

                **kwargs

            )

        return redirect_by_role(request.user)

    return wrapper

def student_required(view_func):

    def wrapper(request, *args, **kwargs):

        if hasattr(request.user, 'userprofile'):

            if request.user.userprofile.role == 'student':
                return view_func(request, *args, **kwargs)

        return redirect('login')

    return wrapper
