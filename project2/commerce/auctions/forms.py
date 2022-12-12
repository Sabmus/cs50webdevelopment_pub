from django import forms
from . import models


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = '__all__'
        exclude = ["owner", "slug", "last_until", "active"]


class CreateBidForm(forms.ModelForm):
    class Meta:
        model = models.Bid
        fields = ["amount", "currency"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ["description"]
