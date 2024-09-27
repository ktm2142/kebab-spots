from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class KebabSpot(models.Model):
    name = models.CharField(max_length=25, verbose_name="Назва", blank=False, null=False)
    location = models.PointField(verbose_name="Розташування", null=False)
    description = models.TextField(verbose_name="Опис", blank=False, null=False)
    notes = models.TextField(verbose_name="Замітки", blank=True)
    payed_or_free = models.BooleanField(verbose_name="Платно", default=False)
    private_property = models.BooleanField(verbose_name="Приватна територія", default=False)
    parking = models.BooleanField(verbose_name="Парковка", default=False)
    toilets = models.BooleanField(verbose_name="Туалети", default=False)
    gazebos = models.BooleanField(verbose_name="Альтанки", default=False)
    tables = models.BooleanField(verbose_name="Столи", default=False)
    camping_places = models.BooleanField(verbose_name="Місце для кемпінгу", default=False)
    swimming_spot = models.BooleanField(verbose_name="Місце для купання", default=False)
    place_for_fire = models.BooleanField(verbose_name="Облаштоване місце для багаття", default=False)
    trash_bins = models.BooleanField(verbose_name="Наявність смітників", default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by", verbose_name="Створено користувачем")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    hidden = models.BooleanField(default=False, verbose_name="Приховано")
    complaints_count = models.PositiveIntegerField(default=0, verbose_name="Кількість скарг")

    def __str__(self):
        return self.name

    def average_rating(self):
        return self.ratings.aggregate(Avg('value'))['value__avg'] or 0

    def star_rating(self):
        avg = self.average_rating()
        return round(avg * 2) / 2


    class Meta:
        verbose_name = "Місце для шашлику"
        verbose_name_plural = "Місця для шашлику"



class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    kebab_spot = models.ForeignKey(KebabSpot, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'kebab_spot')


class KebabSpotPhoto(models.Model):
    kebab_spot = models.ForeignKey(KebabSpot, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='kebab_spots/', blank=True)


class Comment(models.Model):
    kebab_spot = models.ForeignKey(KebabSpot, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class CommentRating(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_ratings')
    is_positive = models.BooleanField(null=True)

    class Meta:
        unique_together = ('comment', 'user')


class CommentPhoto(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_photos')
    image = models.ImageField(upload_to='comment_photos/')


class Complaint(models.Model):
    kebab_spot = models.ForeignKey(KebabSpot, on_delete=models.CASCADE, related_name='complaints')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Текст скарги")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Скарга"
        verbose_name_plural = "Скарги"
        unique_together = ('kebab_spot', 'user')

    def __str__(self):
        return f"Скарга на {self.kebab_spot.name} від {self.user.username}"
