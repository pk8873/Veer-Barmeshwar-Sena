from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Comment, Like, Post
User = get_user_model()

class SocialPlatformTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="adminuser", password="Test-password-42!", is_staff=True)
        self.user = User.objects.create_user(username="member", password="Test-password-42!")
        self.post = Post.objects.create(author=self.staff, title="Public update", body="A community update",
            status=Post.Status.PUBLISHED, published_at=timezone.now())
    def test_published_post_visible(self):
        self.assertContains(self.client.get(reverse("home")), "Public update")
    def test_draft_hidden_from_public(self):
        draft = Post.objects.create(author=self.staff, title="Private draft", body="Secret")
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 404)
    def test_regular_user_cannot_create_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("post_create"), {"title":"forged", "body":"bad", "status":"published"})
        self.assertIn(response.status_code, (302, 403))
        self.assertFalse(Post.objects.filter(title="forged").exists())
    def test_like_toggle_and_uniqueness(self):
        self.client.force_login(self.user)
        url = reverse("toggle_like", kwargs={"slug": self.post.slug})
        self.client.post(url)
        self.assertEqual(Like.objects.filter(post=self.post, user=self.user).count(), 1)
        self.client.post(url)
        self.assertEqual(Like.objects.filter(post=self.post, user=self.user).count(), 0)
    def test_user_cannot_delete_another_users_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.staff, body="Staff comment")
        self.client.force_login(self.user)
        response = self.client.post(reverse("delete_comment", kwargs={"pk": comment.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())
