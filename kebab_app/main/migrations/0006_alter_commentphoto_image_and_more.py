# Generated by Django 5.0.7 on 2024-09-09 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_kebabspot_payed_or_free_comment_commentphoto_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentphoto',
            name='image',
            field=models.ImageField(upload_to='comment_photos/'),
        ),
        migrations.AlterField(
            model_name='commentrating',
            name='is_positive',
            field=models.BooleanField(null=True),
        ),
    ]
