# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-11 17:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0009_auto_20170110_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_course_registration',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
