from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


def get_user_role(user):
    if not user.is_authenticated:
        return None

    try:
        return (user.userprofile.role or "").lower()
    except Exception:
        return "admin" if user.is_superuser else None


def role_guard(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please login to continue.")
                return redirect("login")

            role = get_user_role(request.user)
            if not role:
                messages.error(request, "User profile is missing. Please contact admin.")
                return redirect("login")

            if role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, "You are not authorized to access this page.")
            return redirect("dashboard")

        return wrapper
    return decorator


def admin_only(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login as admin to continue.")
            return redirect("login")

        role = get_user_role(request.user)
        if role == "admin":
            return view_func(request, *args, **kwargs)

        messages.error(request, "Admin access required.")
        logout(request)
        return redirect("login")

    return wrapper


def teacher_only(view_func):
    return role_guard("teacher")(view_func)


def student_only(view_func):
    return role_guard("student")(view_func)


def teacher_or_admin(view_func):
    return role_guard("admin", "teacher")(view_func)


# Backward-compatible names used by existing views.
teacher_required = teacher_only
student_required = student_only
