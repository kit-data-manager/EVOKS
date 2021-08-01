from django import forms

class ProfileForm(forms.Form):
    email = forms.CharField(max_length=100)
    about = forms.CharField(max_length=300)