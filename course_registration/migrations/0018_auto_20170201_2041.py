# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-01 19:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0017_auto_20170201_2035'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_course_progress',
            name='course_id',
        ),
        migrations.AddField(
            model_name='user_course_progress',
            name='iteration_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='course_registration.Course_Iteration'),
            preserve_default=False,
        ),
    ]