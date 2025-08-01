# Generated by Django 5.2.3 on 2025-06-27 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_aboutsection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aboutsection',
            name='icon',
        ),
        migrations.AddField(
            model_name='aboutsection',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='about/'),
        ),
        migrations.AddField(
            model_name='aboutsection',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
