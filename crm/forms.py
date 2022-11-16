from django import forms
from django.contrib.gis.geoip2.resources import Country
from django.core.exceptions import ValidationError

from .models import *
from .validation import validation_ru_letters, validation_phone


class CustomerForm(forms.ModelForm):
    fio_choices = forms.ModelChoiceField(queryset=Customer.objects.all(),
                                         widget=forms.Select(attrs={
                                             'class': 'form-control col',
                                             'name': 'first_name'

                                         }), )

    class Meta:
        model = Customer
        fields = '__all__'

    def clean_last_name(self):
        return validation_ru_letters(self.cleaned_data['last_name'])

    def clean_first_name(self):
        return validation_ru_letters(self.cleaned_data['first_name'])

    def clean_family_name(self):
        return validation_ru_letters(self.cleaned_data['family_name'])

    def clean_phone(self):
        return validation_phone(self.cleaned_data['phone'])


class OrderForm(forms.ModelForm):
    """Создание заказа на первой итерации"""
    class Meta:
        model = Order
        fields = ['title']


class CommentForm(forms.ModelForm):
    text = forms.CharField()
    to = forms.ModelChoiceField(User.objects.all(),
                                      empty_label='Кому')

    class Meta:
        model = Comment
        fields = ['text', 'to']


class TaskForm(forms.ModelForm):
    task = forms.CharField()
    to = forms.ModelChoiceField(User.objects.all(), empty_label='Исполнитель')
    type_task = forms.ModelChoiceField(TypeTask.objects.all(), empty_label='Тип задачи')

    class Meta:
        model = Task
        fields = ['task', 'to', 'deadline', 'type_task']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title']


class MeasuringForm(forms.ModelForm):
    class Meta:
        model = Measuring
        fields = ['measuring']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project']


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ['num_flat', 'num_door', 'num_level', 'num_house', 'num_housing']


class CountryForm(forms.ModelForm):
    class Meta:
        model = AddressCountry
        fields = '__all__'


class AreaForm(forms.ModelForm):
    class Meta:
        model = AddressArea
        fields = '__all__'


class RegionForm(forms.ModelForm):
    class Meta:
        model = AddressRegion
        fields = '__all__'


class TownForm(forms.ModelForm):
    class Meta:
        model = AddressTown
        fields = '__all__'


class StreetForm(forms.ModelForm):
    class Meta:
        model = AddressStreet
        fields = '__all__'

