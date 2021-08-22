from django import forms


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
    name = forms.CharField(label='Full Name', max_length=100)
    email = forms.EmailField(label='Email Address',
                             max_length=254, required=False)
    password = forms.CharField(label='Password', max_length=254)


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(label=("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
