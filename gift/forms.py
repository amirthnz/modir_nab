from django import forms
from gift.models import GiftItem
from django.forms.widgets import FileInput

class GiftForm(forms.ModelForm):
    class Meta:
        model = GiftItem
        fields = ['title', 'description', 'gift_type', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'id':'w3review', 'class':'form-control', 'cols':"40", 'rows':"10"}),
            'gift_type': forms.Select(attrs={'class': 'form-control'}),
            'content': FileInput(attrs={'class': 'file-form-control'}),
        }