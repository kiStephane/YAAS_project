__author__ = 'stephaneki'
from django import forms
from yaasApp.models import *
from django.contrib import admin


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('email',)


class AuctionCreationForm(forms.Form):
    title = forms.CharField(max_length=30)
    description = forms.CharField(widget=forms.Textarea(), required=False)
    creation_date = forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    deadline = forms.DateTimeField(
        help_text="Help")


class ConfirmationForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
    t_title = forms.CharField(widget=forms.HiddenInput())