from django import forms
from django.contrib.auth import authenticate, login, logout

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class LoginForm(forms.Form):
    email = forms.CharField(label="",
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(label="",
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    
    def __init__(self, data=None, files=None, **kwargs):
        super(LoginForm, self).__init__(data, files, kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_show_errors = False
        self.helper.add_input(Submit('submit', 'Login', css_class='btn btn-primary'))
        
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data