from django import forms
import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class RegistrationForm(forms.Form):
    CHOICES = (('Student', 'Student'), ('Private Tutor', 'Private Tutor'), ('Contracted Tutor', 'Contracted Tutor'), ('Student and Contracted Tutor', 'Student and Contracted Tutor'), ('Student and Private Tutor', 'Student and Private Tutor'))
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

class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput()
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput()
    )
    new_password2 = forms.CharField(
        label='New Password(Again)',
        widget=forms.PasswordInput()
    )
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
    def clean_new_password2(self):
        if 'new_password1' in self.cleaned_data:  # when password1 is valid it will exist in self.clean_data
            password1 = self.cleaned_data['new_password1']
            password2 = self.cleaned_data['new_password2']
        if password1 == password2:
            return password2
        raise forms.ValidationError('Passwords do not match.')
    def clean_old_password(self):
        oldPassword = self.cleaned_data['old_password']
        logger.error("compare password")
        logger.error(oldPassword)
        logger.error(self.user.user.password)
        if self.user.user.check_password(oldPassword):
            return oldPassword
        raise forms.ValidationError('Incorrect Password.')

class SearchForm(forms.Form):
    query = forms.CharField(
        label='Enter a keyword to search for',
        widget=forms.TextInput(attrs={'size': 32})
    )
class ProfileForm(forms.Form):
    last_name = forms.CharField(label='Family Name', max_length=50)
    first_name = forms.CharField(label='Given Name', max_length=50)
    phone = forms.CharField(label='Phone Number')
    email = forms.EmailField(label='Email')
    content = forms.CharField(widget=forms.Textarea,label='About Me', max_length=2000)
    image_file = forms.FileField(label='Image', required = False)

'''
class UserProfileForm(forms.Form):
    last_name = forms.CharField(label='Family Name', max_length=30)
    first_name = forms.CharField(label='Given Name', max_length=30)
    email = forms.EmailField(label='Email')
    phone = forms.IntegerField()
    def __init__(self, *args, ):
'''

class PrivateTutorProfileForm(ProfileForm):
    hourly_rate = forms.IntegerField(label='Price')
    def clean_hourly_rate(self):
        price = self.cleaned_data['hourly_rate']
        if price <= 0:
            raise forms.ValidationError('Plase input positive price.')
        elif price % 10 != 0:
                raise forms.ValidationError('Plase input price which is multiple of 10.')
        else:
            return price
'''
class ContractedTutorProfile(UserProfileForm):
    last_name = forms.CharField(label='Family Name', max_length=30)
    first_name = forms.CharField(label='Given Name', max_length=30)
    email = forms.EmailField(label='Email')
    phone = forms.IntegerField()
'''