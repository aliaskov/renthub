from django.db import models
from django.contrib.auth.models import User


# https://dev.to/earthcomfy/django-user-profile-3hik
# https://github.com/earthcomfy/Django-registration-and-login-system.git
class Profile(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
