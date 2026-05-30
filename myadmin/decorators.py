from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('myadmin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('myadmin_login')
            if request.user.role not in roles:
                return HttpResponseForbidden('无权限访问')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
