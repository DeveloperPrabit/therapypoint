# Generated by Django 5.2.3 on 2025-07-02 07:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0025_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='youtube_url',
        ),
        migrations.AddField(
            model_name='video',
            name='video_file',
            field=models.FileField(default=django.utils.timezone.now, upload_to='videos/'),
            preserve_default=False,
        ),
    ]
