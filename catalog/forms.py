from django import forms
from django.forms.widgets import ClearableFileInput
from django.forms import ImageField, FileInput
from catalog.models import Product, Category


class NotClearableImageField(ImageField):
    widget = forms.FileInput

class CustomImageInput(ClearableFileInput):
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control', 'accept': 'image/*', 'form_class': NotClearableImageField}  # Add any default attributes
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'category', 'description', 'link_to_website', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':'عنوان محصول'}),
            'category': forms.Select(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'id':'w3review', 'class':'form-control', 'cols':"40", 'rows':"10"}),
            'link_to_website' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'لینک در وبسایت'}),
            'photo': CustomImageInput(),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':'عنوان دسته بندی'})
        }