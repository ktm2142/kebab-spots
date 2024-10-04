from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class KebabSpot(models.Model):
    name = models.CharField(max_length=25, verbose_name="Name", blank=False, null=False)
    location = models.PointField(verbose_name="Location", null=False)
    description = models.TextField(verbose_name="Description", blank=False, null=False)
    notes = models.TextField(verbose_name="Notes", blank=True)
    payed_or_free = models.BooleanField(verbose_name="Paid or free of charge", default=False)
    private_property = models.BooleanField(verbose_name="Private property", default=False)
    parking = models.BooleanField(verbose_name="Parking", default=False)
    toilets = models.BooleanField(verbose_name="Toilets", default=False)
    gazebos = models.BooleanField(verbose_name="Gazebos", default=False)
    tables = models.BooleanField(verbose_name="Tables", default=False)
    camping_places = models.BooleanField(verbose_name="Camping places", default=False)
    swimming_spot = models.BooleanField(verbose_name="Swimming spot", default=False)
    place_for_fire = models.BooleanField(verbose_name="Place for fire", default=False)
    trash_bins = models.BooleanField(verbose_name="Trash bins", default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by", verbose_name="Created by")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    hidden = models.BooleanField(default=False, verbose_name="Hidden")
    complaints_count = models.PositiveIntegerField(default=0, verbose_name="Complaints count")

    def __str__(self):
        return self.name

    def average_rating(self):
        return self.ratings.aggregate(Avg('value'))['value__avg'] or 0

    def star_rating(self):
        avg = self.average_rating()
        return round(avg * 2) / 2


    class Meta:
        verbose_name = "Kebab spot"
        verbose_name_plural = "Kebab spots"



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
