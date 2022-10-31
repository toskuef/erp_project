from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


def get_first_name(self):
    return f'{self.first_name} {self.last_name}'


User.add_to_class("__str__", get_first_name)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='user')
    status_staff = models.ForeignKey(
        'StatusStaff',
        verbose_name='должность',
        on_delete=models.PROTECT,
        related_name='profile',
    )

    def __str__(self):
        return self.user


class StatusStaff(models.Model):
    status_staff = models.CharField(verbose_name='должность', max_length=20)

    def __str__(self):
        return self.status_staff
