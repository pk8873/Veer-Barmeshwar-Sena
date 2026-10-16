from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="member_profile")
    phone = models.CharField(max_length=10, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_username()} profile"


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="posts")
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    body = models.TextField(max_length=12000)
    image = models.ImageField(upload_to="post_images/%Y/%m/", blank=True)
    video = models.FileField(upload_to="post_videos/%Y/%m/", blank=True)
    image_alt = models.CharField(max_length=240, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT, db_index=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True, db_index=True)
    is_pinned = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:170] or "post"
            candidate, n = base, 2
            while Post.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate, n = f"{base}-{n}", n + 1
            self.slug = candidate
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["post", "user"], name="unique_like_per_user_post")]


class Share(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="shares")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_shares")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="replies")
    body = models.CharField(max_length=2000)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["post", "created_at"])]


class Report(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
    reason = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=80, blank=True)
    object_id = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
