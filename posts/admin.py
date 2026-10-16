from django.contrib import admin
from .models import AuditLog, Comment, Like, MemberProfile, Post, Report, Share


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at", "like_count", "comment_count", "share_count", "is_pinned")
    list_filter = ("status", "is_pinned", "created_at")
    search_fields = ("title", "body", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Likes")
    def like_count(self, obj):
        return obj.likes.count()

    @admin.display(description="Comments")
    def comment_count(self, obj):
        return obj.comments.count()

    @admin.display(description="Shares")
    def share_count(self, obj):
        return obj.shares.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at", "is_hidden")
    list_filter = ("is_hidden", "created_at")
    search_fields = ("body", "author__username", "post__title")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "post", "comment", "resolved", "created_at")
    list_filter = ("resolved", "created_at")
    search_fields = ("reason", "reporter__username")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("post__title", "user__username")
    readonly_fields = ("created_at",)


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("post__title", "user__username")
    readonly_fields = ("created_at",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "object_type", "object_id", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("actor__username", "object_type", "object_id")
    readonly_fields = ("actor", "action", "object_type", "object_id", "created_at", "details")

    def has_add_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "created_at")
    search_fields = ("user__username", "phone")
    readonly_fields = ("created_at",)
