from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from apps.authentication.models import UserProfile


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

        return render(
            request,
            "authentication/login.html",
            {"error": "Invalid username or password"}
        )

    return render(request, "authentication/login.html")


def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        User.objects.create_user(username=username, password=password)
        return redirect("login")

    return render(request, "authentication/register.html")


def logout_page(request):
    logout(request)
    return redirect("login")
