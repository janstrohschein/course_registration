# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-20 15:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0013_auto_20170120_1613'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='seats_cur',
        ),
    ]
