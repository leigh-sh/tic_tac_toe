from django import forms


class SigninForm(forms.Form):
    email = forms.EmailField(label='Email')


class SignupForm(forms.Form):
    email = forms.EmailField(label='Email')
    name = forms.CharField(label='Name', max_length=100)
