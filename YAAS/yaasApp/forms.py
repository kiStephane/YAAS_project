__author__ = 'stephaneki'
from django import forms
from yaasApp.models import *

MINIMUM_AUCTION_DURATION_IN_SECONDS = 72 * 60 * 60  # 72 Hours


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('email',)


class AuctionCreationForm(forms.Form):
    error_messages = {
        'dead_line_not_valid': "Deadline should be at least 72h after creation.",
    }

    title = forms.CharField(max_length=30)
    description = forms.CharField(widget=forms.Textarea(), required=False)
    creation_date = forms.DateTimeField(widget=forms.HiddenInput, initial=datetime.now())
    deadline = forms.DateTimeField(help_text="Format: mm/dd/yy HH:mm:ss | Deadline should be at least"
                                             " 72h after creation")
    minimum_price = forms.IntegerField(min_value=0)

    def clean_deadline(self):
        creation = self.cleaned_data.get('creation_date')
        deadline = self.cleaned_data.get('deadline')
        delta = deadline - creation
        if creation and deadline:
            if delta.total_seconds() < MINIMUM_AUCTION_DURATION_IN_SECONDS:
                raise forms.ValidationError(
                    self.error_messages['dead_line_not_valid'])
        return deadline


class ConfirmationForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)