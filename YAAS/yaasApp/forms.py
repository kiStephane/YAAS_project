__author__ = 'stephaneki'
from django.contrib.auth.models import User
from django import forms


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('email',)