from django.urls import path

from . import views

urlpatterns = [
    path(
        "signup/",
        views.submit_newsletter_signup_form,
        name="submit_newsletter_signup_form",
    ),
]
