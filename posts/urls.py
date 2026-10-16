from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    path("post/<slug:slug>/like/", views.toggle_like, name="toggle_like"),
    path("post/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("post/<slug:slug>/share/", views.share_post, name="share_post"),
    path("comment/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path("post/<slug:slug>/report/", views.report_post, name="report_post"),
    path("manage/", views.dashboard, name="dashboard"),
    path("manage/posts/new/", views.post_create, name="post_create"),
    path("manage/posts/<slug:slug>/edit/", views.post_edit, name="post_edit"),
    path("manage/posts/<slug:slug>/delete/", views.post_delete, name="post_delete"),
]
