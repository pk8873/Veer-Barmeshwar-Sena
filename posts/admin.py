from django.contrib import admin
from .models import AuditLog, Comment, Like, Post, Report
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at", "is_pinned")
    list_filter = ("status", "is_pinned", "created_at")
    search_fields = ("title", "body", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at", "is_hidden")
    list_filter = ("is_hidden",)
    search_fields = ("body", "author__username", "post__title")
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "post", "comment", "resolved", "created_at")
    list_filter = ("resolved",)
admin.site.register(Like)
admin.site.register(AuditLog)
