# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 09:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_course_progress',
            name='progress_reached',
            field=models.BooleanField(default=False),
        ),
    ]
