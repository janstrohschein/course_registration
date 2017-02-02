# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-02 09:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0018_auto_20170201_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_course_registration',
            name='iteration_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='course_registration.Course_Iteration'),
            preserve_default=False,
        ),
    ]
