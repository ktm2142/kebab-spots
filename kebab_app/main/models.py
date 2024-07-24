from django.contrib.auth.models import User
from django.db import models


class KebabSpot(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Довгота")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_spots", verbose_name="Створено користувачем")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Місце для шашлику"
        verbose_name_plural = "Місця для шашлику"
