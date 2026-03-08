"""Accounts forms - Registration, Login, Profile"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    """Custom registration form for farmers"""

    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'province', 'preferred_language', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholder styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.widget.attrs['placeholder'] = field.label or field_name.replace('_', ' ').title()


class LoginForm(AuthenticationForm):
    """Styled login form"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Password'
        })


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'bio',
            'province', 'preferred_language', 'profile_picture',
            'farming_experience', 'crops'
        ]


class AgritexVerificationForm(forms.ModelForm):
    """Form for applying for AGRITEX officer verification"""
    
    confirm_agritex = forms.BooleanField(
        required=True,
        label="I confirm that I am an AGRITEX officer and the document I'm uploading is genuine."
    )

    class Meta:
        model = CustomUser
        fields = ['agritex_id_document']
        widgets = {
            'agritex_id_document': forms.FileInput(attrs={'accept': 'image/*,.pdf'})
        }

    def clean_agritex_id_document(self):
        document = self.cleaned_data.get('agritex_id_document')
        if not document:
            raise forms.ValidationError("Please upload your AGRITEX ID or proof of employment.")
        return document

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'