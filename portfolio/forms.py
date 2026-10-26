from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import CVVersion, FeedPost


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "That username and password did not match.",
        "inactive": "This account is inactive.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "input",
                "autocomplete": "username",
                "placeholder": "Your username",
                "autofocus": True,
                "spellcheck": "false",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "input",
                "autocomplete": "current-password",
                "placeholder": "Your password",
            }
        )


class FeedPostForm(forms.ModelForm):
    class Meta:
        model = FeedPost
        fields = ["content", "image_url"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "input textarea",
                    "rows": 4,
                    "maxlength": 5000,
                    "placeholder": "What are you building, learning, or shipping?",
                    "data-autogrow": "",
                    "data-counter": "5000",
                    "data-counter-target": "composer-counter",
                }
            ),
            "image_url": forms.URLInput(
                attrs={
                    "class": "input",
                    "placeholder": "https://example.com/image.jpg",
                    "inputmode": "url",
                }
            ),
        }

    def clean_content(self):
        content = (self.cleaned_data.get("content") or "").strip()
        if len(content) < 2:
            raise ValidationError("Write something first.")
        if len(content) > 5000:
            raise ValidationError("Keep the post under 5,000 characters.")
        return content

    def clean_image_url(self):
        url = (self.cleaned_data.get("image_url") or "").strip()
        if not url:
            return ""
        validator = URLValidator(schemes=["http", "https"])
        try:
            validator(url)
        except ValidationError:
            raise ValidationError("Use a full http or https image URL.")
        return url


class CVUploadForm(forms.ModelForm):
    class Meta:
        model = CVVersion
        fields = ["file"]
        widgets = {
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "input file-input",
                    "accept": "application/pdf,.pdf",
                }
            )
        }

    def clean_file(self):
        upload = self.cleaned_data.get("file")
        if not upload:
            raise ValidationError("Choose a PDF file.")
        if not upload.name.lower().endswith(".pdf"):
            raise ValidationError("The CV must be a PDF file.")
        if upload.content_type not in ("application/pdf", "application/x-pdf"):
            raise ValidationError("The file does not look like a valid PDF.")
        if upload.size > 10 * 1024 * 1024:
            raise ValidationError("Keep the PDF under 10 MB.")
        return upload
