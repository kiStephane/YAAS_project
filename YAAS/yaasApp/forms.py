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
    title = forms.CharField(label='Title', max_length=30, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                        'placeholder': 'New auction'}))

    description = forms.CharField(label='Description', required=False,
                                  widget=forms.Textarea(attrs={'class': 'form-control'}))

    creation_date = forms.DateTimeField(widget=forms.HiddenInput, initial=timezone.now())
    deadline = forms.DateTimeField(label="Deadline",
                                   help_text="Format: YYYY-mm-dd HH:mm:ss | Deadline should be at least"
                                             " 72h after creation",
                                   widget=forms.TextInput()
                                   )
    minimum_price = forms.FloatField(label='Minimum price', min_value=0,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_deadline(self):
        creation = self.cleaned_data.get('creation_date')
        deadline = self.cleaned_data.get('deadline')
        delta = deadline - creation
        if creation and deadline:
            if delta.total_seconds() < MINIMUM_AUCTION_DURATION_IN_SECONDS:
                raise forms.ValidationError("Deadline should be at least 72h after creation.")
        return deadline


class BidCreationForm(forms.Form):
    auction_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    price = forms.FloatField(label='Minimum price', min_value=0)

    def clean_price(self):
        price = self.cleaned_data.get('price')
        auction_id = self.cleaned_data.get('auction_id')
        auction = Auction.objects.filter(id=auction_id)[0]
        minimum_bid_price = auction.minimum_bid_price()
        if price < minimum_bid_price:
            raise forms.ValidationError("The bid must be superior to the minimum price")
        return price


class ConfirmationForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)