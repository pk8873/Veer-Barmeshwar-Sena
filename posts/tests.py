from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from .models import AuditLog, Comment, Like, MemberProfile, Post, Share

User = get_user_model()


class SocialPlatformTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="adminuser", password="Test-password-42!", is_staff=True)
        self.user = User.objects.create_user(username="member", email="member@example.com", password="Test-password-42!")
        MemberProfile.objects.create(user=self.user, phone="9876543210")
        self.post = Post.objects.create(author=self.staff, title="Public update", body="A community update", status=Post.Status.PUBLISHED, published_at=timezone.now())

    def test_member_can_log_in_with_email(self):
        response = self.client.post(reverse("login"), {"username": "member@example.com", "password": "Test-password-42!"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_member_can_log_in_with_mobile_number(self):
        response = self.client.post(reverse("login"), {"username": "9876543210", "password": "Test-password-42!"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_member_can_register_and_is_logged_in(self):
        response = self.client.post(reverse("register"), {
            "username": "newmember", "phone": "9123456789", "email": "new@example.com",
            "password1": "Long-unique-pass-42!", "password2": "Long-unique-pass-42!",
        })
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(username="newmember")
        self.assertEqual(int(self.client.session["_auth_user_id"]), created.pk)
        self.assertEqual(created.member_profile.phone, "9123456789")
        self.assertFalse(created.is_staff)
        self.assertFalse(created.is_superuser)

    def test_published_post_visible(self):
        self.assertContains(self.client.get(reverse("home")), "Public update")
        self.assertContains(self.client.get(reverse("home")), "cover-peace.svg")

    def test_draft_hidden_from_public(self):
        draft = Post.objects.create(author=self.staff, title="Private draft", body="Secret")
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_regular_user_cannot_create_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("post_create"), {"title": "forged", "body": "bad", "status": "published"})
        self.assertIn(response.status_code, (302, 403))
        self.assertFalse(Post.objects.filter(title="forged").exists())

    def test_like_toggle_and_activity_log(self):
        self.client.force_login(self.user)
        url = reverse("toggle_like", kwargs={"slug": self.post.slug})
        self.client.post(url)
        self.assertEqual(Like.objects.filter(post=self.post, user=self.user).count(), 1)
        self.assertTrue(AuditLog.objects.filter(actor=self.user, action="post_liked").exists())
        self.client.post(url)
        self.assertEqual(Like.objects.filter(post=self.post, user=self.user).count(), 0)
        self.assertTrue(AuditLog.objects.filter(actor=self.user, action="post_unliked").exists())

    def test_ajax_like_returns_json_without_redirect(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("toggle_like", kwargs={"slug": self.post.slug}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["liked"])
        self.assertEqual(response.json()["count"], 1)

    def test_comment_creates_activity_log(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add_comment", kwargs={"slug": self.post.slug}), {"body": "नमस्ते"})
        self.assertTrue(Comment.objects.filter(post=self.post, author=self.user, body="नमस्ते").exists())
        self.assertTrue(AuditLog.objects.filter(actor=self.user, action="comment_added").exists())

    def test_ajax_comment_returns_json_without_redirect(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("add_comment", kwargs={"slug": self.post.slug}),
            {"body": "बढ़िया जानकारी"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["body"], "बढ़िया जानकारी")

    def test_share_requires_login_and_logs_member_share(self):
        url = reverse("share_post", kwargs={"slug": self.post.slug})
        self.assertEqual(self.client.post(url).status_code, 302)
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(url).status_code, 204)
        self.assertEqual(Share.objects.filter(post=self.post, user=self.user).count(), 1)
        self.assertTrue(AuditLog.objects.filter(actor=self.user, action="post_shared").exists())

    def test_user_cannot_delete_another_users_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.staff, body="Staff comment")
        self.client.force_login(self.user)
        response = self.client.post(reverse("delete_comment", kwargs={"pk": comment.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())

    @override_settings(SESSION_COOKIE_AGE=60 * 60 * 24 * 365, SESSION_EXPIRE_AT_BROWSER_CLOSE=False)
    def test_session_is_configured_for_persistent_login(self):
        self.client.force_login(self.user)
        self.assertFalse(self.client.session.get_expire_at_browser_close())
