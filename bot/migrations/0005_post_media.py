# Generated by Django 5.1.2 on 2024-11-10 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_post_media_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='media',
            field=models.FileField(blank=True, null=True, upload_to='media/posts/', verbose_name='تصویر شاخص'),
        ),
    ]
