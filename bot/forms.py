from django import forms
from django.forms.widgets import ClearableFileInput
from django.forms import ImageField, FileInput
from bot.models import Customer, Telebot, Post


class NotClearableImageField(ImageField):
    widget = forms.FileInput

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('has_recieved_gift',)



class CustomImageInput(FileInput):
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'accept': 'image/*, video/*'  # Accepts all image and video file types
        }  # Add any default attributes
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

class RobotForm(forms.ModelForm):
    class Meta:
        model = Telebot
        fields = ['title', 'token', 'welcome_message', 'welcome_picture']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':'عنوان ربات'}),
            'token' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'توکن ربات'}),
            'welcome_message': forms.Textarea(attrs={'id':'w3review', 'class':'form-control', 'cols':"40", 'rows':"10"}),
            'welcome_picture': CustomImageInput(),
        }



class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title','content', 'media']

        widgets = {
            'title': forms.TextInput(attrs={
                'class':'form-control',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',  # Add a CSS class
                'id': 'name-input',
            }),
            'photo' : CustomImageInput(),
            'media': CustomImageInput(),
        }