from django import forms
from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full bg-transparent font-medium text-gray-800 focus:outline-none'}),
        label="Current Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full bg-transparent font-medium text-gray-800 focus:outline-none'}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full bg-transparent font-medium text-gray-800 focus:outline-none'}),
        label="Confirm New Password"
    )
