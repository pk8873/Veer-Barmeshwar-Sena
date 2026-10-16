import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Comment, Post, MemberProfile


def normalize_phone(value):
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    return digits


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="मोबाइल नंबर या नाम",
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username", "placeholder": "मोबाइल नंबर या यूज़रनेम", "inputmode": "text"}),
    )
    password = forms.CharField(
        label="पासवर्ड",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "अपना पासवर्ड लिखें"}),
    )

    def clean(self):
        identifier = (self.cleaned_data.get("username") or "").strip()
        password = self.cleaned_data.get("password")
        if identifier and password:
            UserModel = get_user_model()
            user = UserModel._default_manager.filter(username__iexact=identifier).first()
            if user is None and "@" in identifier:
                user = UserModel._default_manager.filter(email__iexact=identifier).order_by("pk").first()
            if user is None:
                phone = normalize_phone(identifier)
                if len(phone) >= 10:
                    profile = MemberProfile.objects.select_related("user").filter(phone=phone).first()
                    user = profile.user if profile else None
            login_name = user.get_username() if user else identifier
            self.user_cache = authenticate(self.request, username=login_name, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class SimpleMemberCreationForm(UserCreationForm):
    phone = forms.CharField(
        label="मोबाइल नंबर",
        max_length=20,
        widget=forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel", "placeholder": "10 अंकों का मोबाइल नंबर"}),
    )
    email = forms.EmailField(label="ईमेल (वैकल्पिक)", required=False)

    class Meta(UserCreationForm.Meta):
        fields = ("username", "phone", "email", "password1", "password2")
        labels = {"username": "आपका नाम या यूज़रनेम"}

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data.get("phone"))
        if len(phone) != 10:
            raise forms.ValidationError("कृपया 10 अंकों का भारतीय मोबाइल नंबर लिखें।")
        if MemberProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("यह मोबाइल नंबर पहले से रजिस्टर्ड है। लॉगिन करें।")
        return phone


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "maxlength": 2000, "placeholder": "अपनी बात सम्मान के साथ लिखें…"})}


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "image", "video", "image_alt", "status", "scheduled_at", "is_pinned"]
        labels = {
            "title": "Post title",
            "body": "Post content",
            "image": "Post image (JPG, PNG, WebP)",
            "video": "Post video (MP4, WebM, MOV)",
            "image_alt": "Image description (accessibility)",
            "status": "Post status",
            "scheduled_at": "Schedule publication date and time",
            "is_pinned": "Pin this post",
        }
        help_texts = {
            "image": "Upload a new image to replace the current image. Leave empty to keep the current image.",
            "video": "Upload a new video to replace the current video. Leave empty to keep the current video.",
            "image_alt": "Short description of the image for screen readers.",
            "scheduled_at": "Use this for scheduled posts.",
        }
        widgets = {
            "body": forms.Textarea(attrs={"rows": 8}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            if image.size > 8 * 1024 * 1024:
                raise forms.ValidationError("Image must be 8 MB or smaller.")
            if hasattr(image, "content_type") and image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
                raise forms.ValidationError("Upload a JPEG, PNG, or WebP image only.")
        return image

    def clean_video(self):
        video = self.cleaned_data.get("video")
        if video:
            if video.size > 50 * 1024 * 1024:
                raise forms.ValidationError("Video must be 50 MB or smaller.")
            allowed_types = {"video/mp4", "video/webm", "video/quicktime"}
            allowed_extensions = {".mp4", ".webm", ".mov"}
            name = video.name.lower()
            if (hasattr(video, "content_type") and video.content_type not in allowed_types) or not any(name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("Upload an MP4, WebM, or MOV video only.")
        return video
