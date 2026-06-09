from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходимо войти в систему')
            return redirect('login')

        if request.user.profile.role != 'admin':
            messages.error(request, 'У вас нет прав доступа к этой странице')
            return redirect('index')

        return view_func(request, *args, **kwargs)

    return _wrapped_view