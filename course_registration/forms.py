from django import forms
from django.contrib.auth.models import User
from course_registration.models import Course, Progress, Course_Iteration, Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import StrictButton
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
        fields = ('course_id', 'iteration_name', 'course_progress', 'seats_max',
                  'course_active', 'course_registration')

    def __init__(self, *args, **kwargs):
       user = kwargs.pop('user')
       super(TeacherIterationAddForm, self).__init__(*args, **kwargs)
       self.fields['course_id'].queryset = Course.objects.filter(course_teacher =user)


class CourseDetailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        course_iteration_slug = args[0].pop('slug')
        super(CourseDetailForm, self).__init__(*args,**kwargs)

        course_iteration = Course_Iteration.objects.get(slug=course_iteration_slug)
        required_fields = course_iteration.course_id.required_fields.all()

        reg_prefix = 'registration_values_'

        for field in required_fields:
            self.errors[reg_prefix + field.field_name] = self.error_class()

            if field.field_type == 'CharField':
                self.fields[reg_prefix + field.field_name] = forms.CharField(label=field.field_name)

            elif field.field_type == 'EmailField':
                self.fields[reg_prefix + field.field_name] = forms.EmailField(label=field.field_name, max_length=200)

            elif field.field_type == 'BooleanField':
                self.fields[reg_prefix + field.field_name] = forms.BooleanField(label=field.field_name)

            elif field.field_type == 'IntegerField':
                self.fields[reg_prefix + field.field_name] = forms.IntegerField(label=field.field_name)

            elif field.field_type == 'ChoiceField':
                field_choices = field.field_choice_values.split(',')
                field_choice_tuples = [(f, f) for f in field_choices]

                self.fields[reg_prefix + field.field_name] = forms.ChoiceField(label=field.field_name, choices=field_choice_tuples)


class CourseProgressUpdateForm(forms.ModelForm):

    course_progress = forms.ModelChoiceField(queryset=Progress.objects.all(), label='')

    class Meta:
        model = Course_Iteration
        fields = ('course_progress',)

