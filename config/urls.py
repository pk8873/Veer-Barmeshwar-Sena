from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from posts import views as post_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/password-reset/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="password_reset"),
    path("accounts/", include("allauth.urls")),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    path("privacy/", TemplateView.as_view(template_name="pages/privacy.html"), name="privacy"),
    path("terms/", TemplateView.as_view(template_name="pages/terms.html"), name="terms"),
    path("robots.txt", post_views.robots, name="robots"),
]
