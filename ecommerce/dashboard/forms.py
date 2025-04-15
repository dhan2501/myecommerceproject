from django import forms

class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
