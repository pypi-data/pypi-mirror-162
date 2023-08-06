from django import forms

from .models import NewsletterSignUp


class NewsletterSignUpForm(forms.ModelForm):
    class Meta:
        model = NewsletterSignUp
        fields = ["email"]
