from django import forms
import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
class RegistrationForm(forms.Form):
    CHOICES = (('Student', 'Student'), ('Private Tutor', 'Private Tutor'), ('Contracted Tutor', 'Contracted Tutor'))
    identity = forms.ChoiceField(label='Identity',choices=CHOICES)
    username = forms.CharField(label='Username', max_length=30)
    email = forms.EmailField(label='Email')
    last_name = forms.CharField(label='Family Name', max_length=30)
    first_name = forms.CharField(label='Given Name', max_length=30)
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label='Password (Again)',
        widget=forms.PasswordInput()
    )
    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Username can only contain alphanumeric characters and the underscore.')
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('Username is already taken.')

    def clean_password2(self):
        if 'password1' in self.cleaned_data:  # when password1 is valid it will exist in self.clean_data
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
        if password1 == password2:
            return password2
        raise forms.ValidationError('Passwords do not match.')


class SearchForm(forms.Form):
    query = forms.CharField(
        label='Enter a keyword to search for',
        widget=forms.TextInput(attrs={'size': 32})
    )
class ProfileForm(forms.Form):
    last_name = forms.CharField(label='Family Name', max_length=30)
    first_name = forms.CharField(label='Given Name', max_length=30)
    email = forms.EmailField(label='Email')
    phone = forms.IntegerField()
'''
class UserProfileForm(forms.Form):
    last_name = forms.CharField(label='Family Name', max_length=30)
    first_name = forms.CharField(label='Given Name', max_length=30)
    email = forms.EmailField(label='Email')
    phone = forms.IntegerField()
    def __init__(self, *args, ):
'''
'''
class PrivateTutorProfileForm(forms.Form):
    last_name = forms.CharField(label='Family Name', max_length=30)
    first_name = forms.CharField(label='Given Name', max_length=30)
    email = forms.EmailField(label='Email')
    phone = forms.IntegerField()
    hourly_rate = forms.IntegerField()

class ContractedTutorProfile(UserProfileForm):
    last_name = forms.CharField(label='Family Name', max_length=30)
    first_name = forms.CharField(label='Given Name', max_length=30)
    email = forms.EmailField(label='Email')
    phone = forms.IntegerField()
'''