# Generated by Django 5.0.7 on 2024-09-13 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_commentphoto_image_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commentrating',
            old_name='is_positive',
            new_name='vote_type',
        ),
    ]
