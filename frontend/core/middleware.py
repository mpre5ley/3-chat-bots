from django.conf import settings
from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allow = [
            settings.LOGIN_URL,
            "/static/",
            "/admin/",
            "/favicon.ico",
        ]

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        if any(request.path.startswith(p) for p in self.allow):
            return self.get_response(request)

        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
