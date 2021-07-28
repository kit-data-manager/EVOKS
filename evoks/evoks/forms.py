from django import forms
from django.forms.widgets import PasswordInput


class LoginForm(forms.Form):
    """Represents the input necessary to login

    Args:
        forms: Subclasses the Django Form class
    """
    email = forms.CharField(label='Email Address', max_length=254)
    password = forms.CharField(label='Password', max_length=255)


class SignupForm(forms.Form):
    """Represents the input necessary to signup

    Args:
        forms: Subclasses the Django Form class
    """
    #is name optional?
    name = forms.CharField(label='Full Name', max_length=100)
    email = forms.EmailField(label='Email Address',
                             max_length=254, required=False)
    password = forms.CharField(label='Password', max_length=254)

class CreateVocabularyForm(forms.Form):
    """Represents the input for creating a Vocabulary

    Args:
        forms: Subclasses the Django Form class
    """
    voc_name = forms.CharField(label='Vocabulary Name', max_length=100, required=False)
    urispace = forms.CharField(label='URISpace', max_length=100, required=False)
    import_voc = forms.FileField(required=False)
