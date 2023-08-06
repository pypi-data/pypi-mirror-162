from django.contrib import admin

from .models import NewsletterSignUp


class NewsletterSignUpAdmin(admin.ModelAdmin):
    search_fields = ["email"]

    class Meta:
        model = NewsletterSignUp


admin.site.register(NewsletterSignUp, NewsletterSignUpAdmin)
