from django.db import models
from django.utils.text import slugify

# Create your models here.
class User(models.Model):
    user_role = models.CharField(max_length=10, choices=[('user', 'User'), ('teacher', 'Teacher')], default='User')
    user_name = models.CharField(max_length=200, unique=True)
    user_email = models.EmailField(unique=True)

    def __str__(self):
        return self.user_name

class User_Course_Registration(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    field_id = models.ForeignKey('Field', on_delete=models.CASCADE)
    field_value = models.CharField(max_length=200)


class User_Course_Progress(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    user_progress_id = models.ForeignKey('Progress', on_delete=models.CASCADE)
    progress_reached = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        rep = self.course_id.course_name + ', '
        rep += self.user_id.user_name + ', '
        rep += self.user_progress_id.progress_name + ', '
        rep += str(self.progress_reached) + ' ('
        rep += str(self.timestamp) + ')'
        return  rep

class Course(models.Model):
    course_name = models.CharField(max_length=200)
    course_status = models.CharField(max_length= 10, choices=[('active', 'active'), ('inactive', 'inactive')])
    course_progress = models.ForeignKey('Progress', on_delete=models.CASCADE)
    required_fields = models.ManyToManyField('Field')
    slug = models.SlugField(max_length=200, blank=True)

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
    progress_desc = models.CharField(max_length=200)

    def __str__(self):
        return self.progress_name

class Field(models.Model):
    field_name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=200)
    field_desc = models.CharField(max_length=200)

    def __str__(self):
        return self.field_name

# class Field_Required(models.Model):
#     field_id = models.ForeignKey('Field', on_delete=models.CASCADE)
#     course_id = models.ForeignKey('Course', on_delete=models.CASCADE)