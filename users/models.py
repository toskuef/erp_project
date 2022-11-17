from django import forms
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models

User = get_user_model()


def get_first_name(self):
    return f'{self.first_name} {self.last_name}'


User.add_to_class("__str__", get_first_name)


STATUS_CUSTOMER = ((1, 'Неразобран'),
                   (2, 'Новый'),
                   (3, 'Нет активных задач'),
                   (4, 'Есть активные задачи'),
                   (5, 'Действующий'),
                   (6, 'Неактивный'),)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='user')
    status_staff = models.ForeignKey(
        'StatusStaff',
        verbose_name='должность',
        on_delete=models.PROTECT,
        related_name='profile',
        blank=True,
        null=True
    )

    def __str__(self):
        return str(self.user)


class StatusStaff(models.Model):
    status_staff = models.CharField(verbose_name='должность', max_length=20)

    def __str__(self):
        return self.status_staff


class ModifiedArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
            "widget": forms.CheckboxSelectMultiple,
            **kwargs
        }
        return super(ArrayField, self).formfield(**defaults)


class AnySettingsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='settings')
    STATUS_CUSTOMER = ((1, 'Неразобран'),
                       (2, 'Новый'),
                       (3, 'Нет активных задач'),
                       (4, 'Есть активные задачи'),
                       (5, 'Действующий'),
                       (6, 'Неактивный'),)

    filter_customer_list = ModifiedArrayField(
        models.CharField(
            choices=STATUS_CUSTOMER,
            max_length=100,
            blank=True,
            null=True
        ),
        blank=True,
        null=True
    )
    customers_with_active_order = models.BooleanField(default=False)
