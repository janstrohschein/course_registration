from django import forms
from django.contrib.auth.models import User
from course_registration.models import Course, Progress, Course_Iteration, User_Course_Registration
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django.forms.widgets import CheckboxSelectMultiple, ChoiceInput


class MyUserCreationForm(forms.ModelForm):

    email = forms.EmailField(max_length=75, required=True)
    password = forms.CharField(max_length=75, required=True, widget=forms.PasswordInput(), help_text='At least 8 characters')

    class Meta:

        model = User
        fields = ('username', 'email', 'password')


class TeacherCoursesAddForm(forms.ModelForm):

    iteration_name = forms.CharField(max_length=200)
    course_progress = forms.ModelChoiceField(queryset= Progress.objects.all())
    seats_max = forms.IntegerField()

    class Meta:
        model = Course
        fields = ('course_name', 'iteration_name', 'course_progress', 'seats_max', 'required_fields')
        widgets = {"required_fields": CheckboxSelectMultiple(), }

class TeacherIterationAddForm(forms.ModelForm):

    class Meta:
        model = Course_Iteration
        fields = ('course_id', 'iteration_name', 'course_active',
              'course_registration', 'course_progress', 'seats_max')

    def __init__(self, *args, **kwargs):
       user = kwargs.pop('user')
       super(TeacherIterationAddForm, self).__init__(*args, **kwargs)
       self.fields['course_id'].queryset = Course.objects.filter(course_teacher =user)


class CourseDetailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        course_iteration_slug = kwargs.pop('course_slug')
        super(CourseDetailForm, self).__init__(*args,**kwargs)

        course_iteration = Course_Iteration.objects.get(slug=course_iteration_slug)
        required_fields = course_iteration.course_id.required_fields.all()

        for field in required_fields:
            t = 't'
            if field.field_type == 'CharField':
                self.fields[field.field_name] = forms.CharField(label=field.field_name, required=True)

            elif field.field_type == 'EmailField':
                self.fields[field.field_name] = forms.EmailField(max_length=200, required= True)

            elif field.field_type == 'BooleanField':
                self.fields[field.field_name] = forms.BooleanField(required=True)

            elif field.field_type == 'IntegerField':
                self.fields[field.field_name] = forms.IntegerField(required=True)

            elif field.field_type == 'ChoiceField':
                field_choices = field.field_choice_values.split(',')
                field_choice_tuples = [(f, f) for f in field_choices]

                self.fields[field.field_name] = forms.ChoiceField(choices=field_choice_tuples, required=True)


class CourseProgressUpdateForm(forms.ModelForm):

    course_progress = forms.ModelChoiceField(queryset=Progress.objects.all(), label='')

    class Meta:
        model = Course_Iteration
        fields = ('course_progress',)

