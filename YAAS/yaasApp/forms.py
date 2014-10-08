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
        'deadline': "Deadline should be at least 72h after creation.",
    }

    title = forms.CharField(label='Title', max_length=30)
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)
    creation_date = forms.DateTimeField(widget=forms.HiddenInput, initial=timezone.now())
    deadline = forms.DateTimeField(label='Deadline', help_text="Format: mm/dd/yy HH:mm:ss | Deadline should be at least"
                                                               " 72h after creation")
    minimum_price = forms.FloatField(label='Minimum price', min_value=0)

    def clean_deadline(self):
        creation = self.cleaned_data.get('creation_date')
        deadline = self.cleaned_data.get('deadline')
        delta = deadline - creation
        if creation and deadline:
            if delta.total_seconds() < MINIMUM_AUCTION_DURATION_IN_SECONDS:
                raise forms.ValidationError(self.error_messages['deadline'])
        return deadline


class BidCreationForm(forms.Form):
    auction_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    price = forms.FloatField(label='Minimum price', min_value=0)

    def clean_price(self):
        price = self.cleaned_data.get('price')
        auction_id = self.cleaned_data.get('auction_id')
        auction = Auction.objects.filter(id=auction_id)[0]
        last_bid_price = auction.last_bid_price()
        if price < (last_bid_price + 0.01):
            raise forms.ValidationError("The bid must be superior to the minimum price")
        return price


class ConfirmationForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)