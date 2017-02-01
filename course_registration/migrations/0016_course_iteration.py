# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-01 19:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_registration', '0015_remove_user_course_progress_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course_Iteration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iteration_name', models.CharField(max_length=200)),
                ('course_active', models.BooleanField(default=True)),
                ('course_registration', models.BooleanField(default=True)),
                ('seats_max', models.IntegerField()),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.Course')),
                ('course_progress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.Progress')),
            ],
        ),
    ]
