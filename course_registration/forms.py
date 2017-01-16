from django import forms
from django.contrib.auth.models import User
from course_registration.models import Course
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django.forms.widgets import CheckboxSelectMultiple


class MyUserCreationForm(forms.ModelForm):

    email = forms.EmailField(max_length=75, required=True)
    password = forms.CharField(max_length=75, required=True, widget=forms.PasswordInput(), help_text='At least 8 characters')

    class Meta:

        model = User
        fields = ('username', 'email', 'password')


class TeacherCoursesAddForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ('course_name', 'course_progress', 'seats_max', 'required_fields')
        widgets = {"required_fields": CheckboxSelectMultiple(), }



