from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string


class ActivationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, user):
        token = get_random_string(length=64)
        return cls.objects.create(user=user, token=token)

