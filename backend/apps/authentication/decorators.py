from django.shortcuts import redirect

from django.http import HttpResponse


# ==============================
# ADMIN ONLY
# ==============================

def admin_only(view_func):

    def wrapper(request, *args, **kwargs):

        if request.user.is_superuser:

            return view_func(

                request,
                *args,
                **kwargs

            )

        return HttpResponse(

            "Access Denied"

        )

    return wrapper