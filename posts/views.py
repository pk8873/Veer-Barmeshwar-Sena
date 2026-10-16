from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from .forms import CommentForm, PostForm
from .models import AuditLog, Comment, Like, Post, Report

def public_posts():
    now = timezone.now()
    return Post.objects.filter(status=Post.Status.PUBLISHED, published_at__lte=now).select_related("author").prefetch_related("likes", "comments")

def home(request):
    qs = public_posts()
    term = request.GET.get("q", "").strip()
    if term:
        qs = qs.filter(Q(title__icontains=term) | Q(body__icontains=term))
    page = Paginator(qs, 8).get_page(request.GET.get("page"))
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(Like.objects.filter(user=request.user, post__in=page.object_list).values_list("post_id", flat=True))
    return render(request, "posts/home.html", {"page": page, "liked_ids": liked_ids, "query": term})

def post_detail(request, slug):
    post = get_object_or_404(public_posts(), slug=slug)
    comments = post.comments.filter(is_hidden=False, parent__isnull=True).select_related("author").prefetch_related("replies__author")
    liked = request.user.is_authenticated and post.likes.filter(user=request.user).exists()
    form = CommentForm()
    return render(request, "posts/detail.html", {"post": post, "comments": comments, "liked": liked, "form": form})

@login_required
@require_POST
def toggle_like(request, slug):
    post = get_object_or_404(public_posts(), slug=slug)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return redirect(request.POST.get("next") or post.get_absolute_url())

@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(public_posts(), slug=slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        Comment.objects.create(post=post, author=request.user, body=strip_tags(form.cleaned_data["body"]).strip())
    else:
        messages.error(request, "Please check your comment and try again.")
    return redirect(post.get_absolute_url() + "#comments")

@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(Comment.objects.select_related("author"), pk=pk)
    if comment.author_id != request.user.id and not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    post_url = comment.post.get_absolute_url()
    comment.delete()
    return redirect(post_url + "#comments")

@login_required
@require_POST
def report_post(request, slug):
    post = get_object_or_404(public_posts(), slug=slug)
    reason = strip_tags(request.POST.get("reason", "")).strip()[:500]
    if reason:
        Report.objects.create(reporter=request.user, post=post, reason=reason)
        messages.success(request, "Thank you. Your report has been submitted for review.")
    return redirect(post.get_absolute_url())

def staff_required(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(staff_required)
def dashboard(request):
    return render(request, "posts/dashboard.html", {
        "post_count": Post.objects.count(), "published_count": public_posts().count(),
        "comment_count": Comment.objects.count(), "report_count": Report.objects.filter(resolved=False).count(),
        "recent_posts": Post.objects.select_related("author")[:8],
    })

@user_passes_test(staff_required)
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        if post.status == Post.Status.PUBLISHED:
            post.published_at = timezone.now()
        post.save()
        AuditLog.objects.create(actor=request.user, action="post_created", object_type="Post", object_id=str(post.pk))
        messages.success(request, "Post saved.")
        return redirect("dashboard")
    return render(request, "posts/post_form.html", {"form": form, "heading": "Create a post"})

@user_passes_test(staff_required)
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        updated = form.save(commit=False)
        if updated.status == Post.Status.PUBLISHED and not updated.published_at:
            updated.published_at = timezone.now()
        updated.save()
        AuditLog.objects.create(actor=request.user, action="post_updated", object_type="Post", object_id=str(post.pk))
        messages.success(request, "Post updated.")
        return redirect("dashboard")
    return render(request, "posts/post_form.html", {"form": form, "heading": "Edit post"})

@user_passes_test(staff_required)
@require_POST
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    AuditLog.objects.create(actor=request.user, action="post_deleted", object_type="Post", object_id=str(post.pk))
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("dashboard")

def robots(request):
    return HttpResponse("User-agent: *\nDisallow: /admin/\n", content_type="text/plain")
