from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import sys


class User_Course_Registration(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    field_id = models.ForeignKey('Field', on_delete=models.CASCADE)
    field_value = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        rep = self.course_id.course_name + ', '
        rep += self.user_id.username + ', '
        rep += self.field_id.field_name + ', '
        rep += self.field_value + ' ('
        rep += str(self.timestamp) + ')'
        return  rep

    class Meta:
        ordering = ['id']


class User_Course_Progress(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    user_progress_id = models.ForeignKey('Progress', on_delete=models.CASCADE)
    progress_reached = models.BooleanField(default=False)
    #active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        rep = self.course_id.course_name + ', '
        rep += self.user_id.username + ', '
        rep += self.user_progress_id.progress_name + ', '
        rep += str(self.progress_reached)  + ', '
        rep += str(self.active) + ' ('
        rep += str(self.timestamp) + ')'
        return  rep


class Course(models.Model):
    course_name = models.CharField(max_length=200)
    course_teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    course_active = models.BooleanField(default=True)
    course_registration = models.BooleanField(default=True)
    course_progress = models.ForeignKey('Progress', on_delete=models.CASCADE)
    seats_max = models.IntegerField()
    required_fields = models.ManyToManyField('Field')
    slug = models.SlugField(max_length=200, blank=True)

    @property
    def seats_cur(self):
        seats_cur = User_Course_Registration.objects.filter(course_id=self.id)\
            .values('user_id').annotate(user_count = models.Count('user_id')).count()
        return seats_cur

    def __str__(self):
        return self.course_name

    def _get_unique_slug(self):
        slug = slugify(self.course_name)
        unique_slug = slug
        num = 1
        while Course.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save()


class Progress(models.Model):
    progress_name = models.CharField(max_length=200)
    progress_desc = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.progress_name


class Field(models.Model):
    field_name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=200)
    field_desc = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.field_name


### introduce new class course iteration