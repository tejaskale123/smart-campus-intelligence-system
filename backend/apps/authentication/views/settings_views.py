from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from apps.authentication.decorators import (
    admin_only,
)


@login_required
@admin_only
def settings_page(request):
    if request.method == "POST":
        campus_name = (request.POST.get("campus_name") or "").strip()
        theme = (request.POST.get("theme") or "").strip()
        email = (request.POST.get("admin_email") or "").strip()
        password = (request.POST.get("password") or "")

        request.session["campus_name"] = campus_name or "Smart Campus"
        request.session["theme"] = theme or "Dark"

        if email:
            request.user.email = email

        if password:
            request.user.set_password(password)
            messages.info(request, "Password updated. Please login again.")
            request.user.save()
            logout(request)
            return redirect("login")

        request.user.save()
        messages.success(request, "Settings saved successfully.")
        return redirect("settings")

    return render(
        request,
        "dashboard/settings.html",
        {
            "campus_name": request.session.get("campus_name", "Smart Campus"),
            "theme": request.session.get("theme", "Dark"),
        }
    )
