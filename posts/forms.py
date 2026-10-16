from django import forms
from .models import Comment, Post
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "maxlength": 2000, "placeholder": "Add a respectful comment…"})}
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "image", "image_alt", "status", "scheduled_at", "is_pinned"]
        widgets = {"body": forms.Textarea(attrs={"rows": 8}), "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}
    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            if image.size > 8 * 1024 * 1024:
                raise forms.ValidationError("Images must be 8 MB or smaller.")
            if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
                raise forms.ValidationError("Upload a JPEG, PNG, or WebP image.")
        return image
