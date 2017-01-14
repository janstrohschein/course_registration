from django import forms
from django.contrib.auth.models import User


class MyUserCreationForm(forms.ModelForm):

    email = forms.EmailField(max_length=75, required=True)


    class Meta:

        model = User
        fields = ('username', 'email', 'password')
