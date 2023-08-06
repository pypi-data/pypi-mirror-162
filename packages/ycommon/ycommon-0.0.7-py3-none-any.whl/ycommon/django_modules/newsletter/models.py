from django.db import models


class NewsletterSignUp(models.Model):
    email = models.EmailField(max_length=1000, blank=False, null=False, unique=True)
    registered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
