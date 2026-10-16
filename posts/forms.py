from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Comment, Post


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="ईमेल या यूज़रनेम",
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="पासवर्ड",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            UserModel = get_user_model()
            if "@" in username:
                matched_user = UserModel._default_manager.filter(email__iexact=username).order_by("pk").first()
                if matched_user:
                    username = matched_user.get_username()
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class SimpleMemberCreationForm(UserCreationForm):
    email = forms.EmailField(label="ईमेल (वैकल्पिक)", required=False)

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email", "password1", "password2")
        labels = {"username": "यूज़रनेम"}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "maxlength": 2000, "placeholder": "अपनी बात सम्मान के साथ लिखें…"})}


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "image", "video", "image_alt", "status", "scheduled_at", "is_pinned"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 8}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            if image.size > 8 * 1024 * 1024:
                raise forms.ValidationError("तस्वीर 8 MB या उससे छोटी होनी चाहिए।")
            if hasattr(image, "content_type") and image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
                raise forms.ValidationError("केवल JPEG, PNG या WebP तस्वीर अपलोड करें।")
        return image

    def clean_video(self):
        video = self.cleaned_data.get("video")
        if video:
            if video.size > 50 * 1024 * 1024:
                raise forms.ValidationError("वीडियो 50 MB या उससे छोटा होना चाहिए।")
            allowed_types = {"video/mp4", "video/webm", "video/quicktime"}
            allowed_extensions = {".mp4", ".webm", ".mov"}
            name = video.name.lower()
            if (hasattr(video, "content_type") and video.content_type not in allowed_types) or not any(name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("केवल MP4, WebM या MOV वीडियो अपलोड करें।")
        return video
