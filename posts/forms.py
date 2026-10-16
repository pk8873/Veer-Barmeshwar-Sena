from django import forms
from .models import Comment, Post


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
