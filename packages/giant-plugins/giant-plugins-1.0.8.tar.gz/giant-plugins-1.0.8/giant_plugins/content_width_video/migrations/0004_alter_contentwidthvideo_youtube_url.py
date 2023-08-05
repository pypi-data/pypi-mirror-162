# Generated by Django 3.2.13 on 2022-07-28 10:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_width_video', '0003_auto_20220621_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentwidthvideo',
            name='youtube_url',
            field=models.URLField(blank=True, help_text="\n            Enter the full URL of the youtube video page. \n            To start the video at a specific time add '&t=xx' to the end of the url (using seconds). \n            You can also add extra paramaters using an ampersand, for example '&t=75&autoplay=1'.\n        ", null=True, validators=[django.core.validators.URLValidator(message='Please enter the full URL of the Youtube video page', regex='www.youtube.com', schemes=['https'])]),
        ),
    ]
