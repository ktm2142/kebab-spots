# Generated by Django 5.0.7 on 2024-09-26 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            CREATE INDEX gin_index_title ON recipes_recipe USING gin (title gin_trgm_ops);
            CREATE INDEX gin_index_description ON recipes_recipe USING gin (description gin_trgm_ops);
            CREATE INDEX gin_index_ingredients ON recipes_recipe USING gin (ingredients gin_trgm_ops);
            ''',
            reverse_sql='''
            DROP INDEX IF EXISTS gin_index_title;
            DROP INDEX IF EXISTS gin_index_description;
            DROP INDEX IF EXISTS gin_index_ingredients;
            DROP EXTENSION IF EXISTS pg_trgm;
            '''
        ),
    ]
