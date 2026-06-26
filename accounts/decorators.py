from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Activite, User


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_admin:
                return view_func(request, *args, **kwargs)
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Accès non autorisé.')
            return redirect('accounts:dashboard')
        return wrapper
    return decorator


def log_activity(user, action, module):
    if user and user.is_authenticated:
        Activite.objects.create(utilisateur=user, action=action, module=module)
