from django.conf import settings


def auth_options(request):
    return {"GOOGLE_LOGIN_ENABLED": settings.GOOGLE_LOGIN_ENABLED}
