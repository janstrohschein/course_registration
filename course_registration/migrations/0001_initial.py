# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-02 19:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(max_length=200)),
                ('course_status', models.CharField(choices=[('active', 'active'), ('inactive', 'inactive')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=200)),
                ('field_type', models.CharField(max_length=200)),
                ('field_desc', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress_name', models.CharField(max_length=200)),
                ('progress_desc', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_role', models.CharField(choices=[('user', 'User'), ('teacher', 'Teacher')], default='User', max_length=10)),
                ('user_name', models.CharField(max_length=200, unique=True)),
                ('user_email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='User_Course_Progress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.Course')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.User')),
                ('user_progress_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.Progress')),
            ],
        ),
        migrations.CreateModel(
            name='User_Course_Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_value', models.CharField(max_length=200)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.Course')),
                ('field_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.Field')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.User')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='course_progress',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_registration.Progress'),
        ),
        migrations.AddField(
            model_name='course',
            name='required_fields',
            field=models.ManyToManyField(to='course_registration.Field'),
        ),
    ]
