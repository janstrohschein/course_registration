from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import sys


class User_Course_Registration(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    iteration_id = models.ForeignKey('Course_Iteration', on_delete=models.CASCADE)
    field_id = models.ForeignKey('Field', on_delete=models.CASCADE)
    field_value = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        rep = self.course_id.course_name + ', '
        rep += ' (' + self.iteration_id.iteration_name + '), '
        rep += self.user_id.username + ', '
        rep += self.field_id.field_name + ', '
        rep += self.field_value + ' ('
        rep += str(self.timestamp) + ')'
        return  rep

    class Meta:
        ordering = ['id']


class User_Course_Progress_Manager(models.Manager):
    def lowest_unfinished(self):
        """
        Finds the lowest unfinished or last Progress Entry for a user/course combination.

        :return:
        """
        #courses = User_Course_Progress.objects.filter(iteration_id__course_active=True).order_by('user_id', 'iteration_id')
        courses = User_Course_Progress.objects.all().order_by('user_id', 'iteration_id')
        user_id = 0
        course_id = 0
        reduced_courses = []
        course_appended = False
        for index, course in enumerate(reversed(courses)):
            next_index = len(courses) - (index + 2)

            if user_id != course.user_id_id:
                user_id = course.user_id_id
                course_appended = False

            if course_id != course.iteration_id_id:
                course_appended = False
                course_id = course.iteration_id_id

            if course.progress_reached == True and course_appended == False:
                course_appended = True
                reduced_courses.append(course.id)

            elif course_appended == False and (next_index < 0):
                course_appended = True
                reduced_courses.append(course.id)

            elif course_appended == False and courses[next_index].iteration_id_id != course_id:
                course_appended = True
                reduced_courses.append(course.id)

            elif course_appended == False and courses[next_index].user_id_id != user_id:
                course_appended = True
                reduced_courses.append(course.id)

            elif course_appended == False and courses[next_index].iteration_id_id == course_id \
                    and courses[next_index].progress_reached == True:
                course_appended = True
                reduced_courses.append(course.id)

        return User_Course_Progress.objects.filter(id__in=reduced_courses)


class User_Course_Progress(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    iteration_id = models.ForeignKey('Course_Iteration', on_delete=models.CASCADE)
    user_progress_id = models.ForeignKey('Progress', on_delete=models.CASCADE)
    progress_reached = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    objects = User_Course_Progress_Manager()

    def __str__(self):
        rep = self.iteration_id.course_id.course_name + ', '
        rep += self.user_id.username + ', '
        rep += self.user_progress_id.progress_name + ', '
        rep += str(self.progress_reached)  + ' ('
        rep += str(self.timestamp) + ')'
        return  rep


class Course(models.Model):
    course_name = models.CharField(max_length=200)
    course_teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    required_fields = models.ManyToManyField('Field')
    slug = models.SlugField(max_length=200, blank=True)

    # course_active = models.BooleanField(default=True)
    # course_registration = models.BooleanField(default=True)
    # course_progress = models.ForeignKey('Progress', on_delete=models.CASCADE)
    # seats_max = models.IntegerField()
    #
    # @property
    # def seats_cur(self):
    #     seats_cur = User_Course_Registration.objects.filter(course_id=self.id)\
    #         .values('user_id').annotate(user_count = models.Count('user_id')).count()
    #     return seats_cur

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


class Course_Iteration(models.Model):

    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    iteration_name = models.CharField(max_length=200)
    course_active = models.BooleanField(default=True)
    course_registration = models.BooleanField(default=True)
    course_progress = models.ForeignKey('Progress', on_delete=models.CASCADE)
    seats_max = models.IntegerField()
    slug = models.SlugField(max_length=200, blank=True)

    @property
    def seats_cur(self):
        seats_cur = User_Course_Registration.objects.filter(iteration_id=self.id)\
            .values('user_id').annotate(user_count = models.Count('user_id')).count()
        return seats_cur

    def _get_unique_slug(self):
        course_slug = Course.objects.get(id = self.course_id_id)
        slug = course_slug.slug +'-' + slugify(self.iteration_name)
        unique_slug = slug
        num = 1
        while Course_Iteration.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save()


    def __str__(self):
        repstring = self.course_id.course_name
        repstring += ' (' + self.slug + ')'

        return repstring


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