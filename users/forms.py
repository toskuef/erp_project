from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from users.models import AnySettingsUser

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class UserSettingsStatusCustomerForm(forms.ModelForm):
    class Meta:
        model = AnySettingsUser
        fields = ['filter_customer_list']
