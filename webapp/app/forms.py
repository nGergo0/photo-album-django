from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['name', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 40}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
