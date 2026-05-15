from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout

from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib.auth.models import User

from apps.authentication.models import UserProfile


def login_page(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            profile = UserProfile.objects.get(
                user=user
            )

            if profile.role == "admin":
                return redirect("admin_dashboard")

            if profile.role == "teacher":
                return redirect("teacher_dashboard")

            return redirect("student_dashboard")

        return render(
            request,
            "authentication/login.html",
            {
                "error": "Invalid username or password"
            }
        )

    return render(
        request,
        "authentication/login.html"
    )


def register_page(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect("login")

    return render(
        request,
        "authentication/register.html"
    )


def logout_page(request):

    logout(request)

    return redirect("login")