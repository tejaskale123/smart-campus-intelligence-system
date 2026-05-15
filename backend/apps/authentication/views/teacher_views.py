from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from apps.authentication.models import UserProfile
from apps.authentication.decorators import (
    admin_only,
)


@login_required
@admin_only
def admin_teachers(request):
    teachers = (
        UserProfile.objects
        .select_related("user")
        .filter(role="teacher")
        .order_by("user__username")
    )

    return render(
        request,
        "teachers/teachers_list.html",
        {"teachers": teachers}
    )


@login_required
@admin_only
def add_teacher(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        department = (request.POST.get("department") or "").strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("add_teacher")

        teacher_user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        profile = teacher_user.userprofile
        profile.role = "teacher"
        profile.department = department
        profile.save()

        messages.success(request, "Teacher created successfully.")
        return redirect("admin_teachers")

    return render(request, "teachers/add_teacher.html")


@login_required
@admin_only
def update_teacher(request, teacher_id):
    profile = get_object_or_404(
        UserProfile.objects.select_related("user"),
        id=teacher_id,
        role="teacher"
    )

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        department = (request.POST.get("department") or "").strip()

        if (
            User.objects
            .filter(username=username)
            .exclude(id=profile.user.id)
            .exists()
        ):
            messages.error(request, "Username already exists.")
            return redirect("update_teacher", teacher_id=profile.id)

        profile.user.username = username
        profile.user.email = email
        if password:
            profile.user.set_password(password)
        profile.user.save()

        profile.department = department
        profile.save()

        messages.success(request, "Teacher updated successfully.")
        return redirect("admin_teachers")

    return render(
        request,
        "teachers/add_teacher.html",
        {"teacher": profile, "is_update": True}
    )


@login_required
@admin_only
def delete_teacher(request, teacher_id):
    profile = get_object_or_404(UserProfile, id=teacher_id, role="teacher")
    profile.user.delete()
    messages.success(request, "Teacher deleted successfully.")
    return redirect("admin_teachers")
