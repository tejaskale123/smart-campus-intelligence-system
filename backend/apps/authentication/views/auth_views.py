from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from apps.authentication.models import UserProfile
from database.mongo import db


LOGIN_LOGS = db["login_logs"]
SECURITY_LOGS = db["security_logs"]
USERS_COLLECTION = db["users"]


def _log_login(request, user, role):
    try:
        LOGIN_LOGS.insert_one({
            "username": user.username,
            "role": role,
            "login_time": datetime.now(),
            "ip_address": request.META.get("REMOTE_ADDR"),
        })
    except Exception as error:
        print("Login Log Error:", error)


def _log_security_event(request, event, username=None):
    try:
        SECURITY_LOGS.insert_one({
            "event": event,
            "username": username,
            "ip_address": request.META.get("REMOTE_ADDR"),
            "created_at": datetime.now(),
        })
    except Exception as error:
        print("Security Log Error:", error)


def home(request):
    return render(request, "base/base.html")


def login_page(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            logout(request)
            return render(
                request,
                "authentication/login.html",
                {"error": "Profile not found. Please contact admin."}
            )

        if profile.role == "admin":
            return redirect("admin_dashboard")
        if profile.role == "teacher":
            return redirect("teacher_dashboard")
        if profile.role == "student":
            return redirect("student_dashboard")

        logout(request)
        return render(
            request,
            "authentication/login.html",
            {"error": "Invalid role assigned. Please contact admin."}
        )

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                logout(request)
                return render(
                    request,
                    "authentication/login.html",
                    {"error": "Profile not found. Please contact admin."}
                )

            _log_login(request, user, profile.role)

            if profile.role == "admin":
                return redirect("admin_dashboard")
            if profile.role == "teacher":
                return redirect("teacher_dashboard")
            if profile.role == "student":
                return redirect("student_dashboard")

            logout(request)
            return render(
                request,
                "authentication/login.html",
                {"error": "Invalid role assigned. Please contact admin."}
            )

        _log_security_event(request, "Failed Login", username)

        return render(
            request,
            "authentication/login.html",
            {"error": "Invalid username or password"}
        )

    return render(request, "authentication/login.html")


def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = (request.POST.get("email") or "").strip()
        role = (request.POST.get("role") or "student").strip()
        password = request.POST.get("password")
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        try:
            USERS_COLLECTION.insert_one({
                "username": username,
                "email": email,
                "role": role,
                "user_id": str(user.id),
                "created_at": datetime.now(),
            })
            print("USER SAVED IN MONGO")
        except Exception as error:
            print("User Mongo Save Error:", error)

        return redirect("login")

    return render(request, "authentication/register.html")


def logout_page(request):
    logout(request)
    return redirect("login")
