import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from users.models import AnySettingsUser

User = get_user_model()
STATUS_CUSTOMER = AnySettingsUser.STATUS_CUSTOMER


def get_first_name(self):
    return f'{self.first_name} {self.last_name}'


User.add_to_class("__str__", get_first_name)


class Customer(models.Model):
    last_name = models.CharField(max_length=100, verbose_name='фамилия')
    first_name = models.CharField(max_length=100, verbose_name='имя')
    family_name = models.CharField(max_length=100, verbose_name='отчество')
    phone = models.CharField(max_length=15, verbose_name='номер телефона')
    date = models.DateTimeField(auto_now_add=True,
                                verbose_name='дата создания',
                                blank=True, null=True)
    creater_customer = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='customers',
        blank=True,
        null=True
    )
    source = models.ForeignKey(
        'SourceCustomer',
        related_name='customers',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Источник',
    )
    comments = GenericRelation('Comment')
    tasks = GenericRelation('Task')
    is_show = models.BooleanField(default=False)
    status_customer = models.IntegerField(choices=STATUS_CUSTOMER,
                                          default=1)
    is_active_order = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'
        ordering = ['-date']

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.family_name}'

    def get_my_model_name(self):
        return self._meta.model_name


class SourceCustomer(models.Model):
    source = models.CharField(max_length=15, verbose_name='Источник')

    def __str__(self):
        return self.source


class Address(models.Model):
    customer = models.ManyToManyField(
        'Customer',
        verbose_name='клиенты',
        related_name='addresses',
        blank=True,
    )
    country = models.ForeignKey(
        'AddressCountry',
        on_delete=models.PROTECT,
        related_name='addresses',
        verbose_name='страна',
        blank=True,
        null=True
    )
    area = models.ForeignKey(
        'AddressArea',
        on_delete=models.PROTECT,
        related_name='addresses',
        verbose_name='область',
        blank=True,
        null=True
    )
    region = models.ForeignKey(
        'AddressRegion',
        on_delete=models.PROTECT,
        related_name='addresses',
        verbose_name='район',
        blank=True,
        null=True

    )
    town = models.ForeignKey(
        'AddressTown',
        on_delete=models.PROTECT,
        related_name='addresses',
        verbose_name='город',
        blank=True,
        null=True
    )
    street = models.ForeignKey(
        'AddressStreet',
        on_delete=models.PROTECT,
        related_name='addresses',
        verbose_name='улица',
        null=True,
        blank=True
    )
    num_house = models.CharField(verbose_name='номер дома', max_length=10,
                                 blank=True, null=True)
    num_housing = models.IntegerField(verbose_name='номер корпуса', blank=True,
                                      null=True)
    num_door = models.IntegerField(verbose_name='номер подъезда', blank=True,
                                   null=True)
    num_level = models.IntegerField(verbose_name='номер этажа', blank=True,
                                    null=True)
    num_flat = models.IntegerField(verbose_name='номер квартиры', blank=True,
                                   null=True)

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'адреса'

    def __str__(self):
        return (f'{self.country}, {self.area}, {self.region}, {self.town}, '
                f'{self.street}, {self.num_house}, {self.num_housing}, '
                f'{self.num_door}, {self.num_level}, {self.num_flat}')


class AddressCountry(models.Model):
    country_title = models.CharField(verbose_name='назавние страны', max_length=100)

    class Meta:
        verbose_name = 'страна'
        verbose_name_plural = 'страны'

    def __str__(self):
        return self.country_title


class AddressArea(models.Model):
    area_title = models.CharField(verbose_name='назавние области', max_length=100)

    class Meta:
        verbose_name = 'область'
        verbose_name_plural = 'области'

    def __str__(self):
        return self.area_title


class AddressRegion(models.Model):
    region_title = models.CharField(verbose_name='название района', max_length=100)

    class Meta:
        verbose_name = 'район'
        verbose_name_plural = 'районы'

    def __str__(self):
        return self.region_title


class AddressTown(models.Model):
    town_title = models.CharField(verbose_name='название города', max_length=100)

    class Meta:
        verbose_name = 'город'
        verbose_name_plural = 'города'

    def __str__(self):
        return self.town_title


class AddressStreet(models.Model):
    street_title = models.CharField(verbose_name='название улицы', max_length=100)

    class Meta:
        verbose_name = 'улица'
        verbose_name_plural = 'улицы'

    def __str__(self):
        return self.street_title


class Order(models.Model):
    title = models.CharField(max_length=150, verbose_name='название')
    price = models.DecimalField(decimal_places=2, max_digits=20,
                                verbose_name='сумма заказа', blank=True, null=True)
    pre_pay = models.DecimalField(decimal_places=2, max_digits=20,
                                  verbose_name='предоплата', blank=True, null=True)
    second_pay = models.DecimalField(decimal_places=2, max_digits=20,
                                     verbose_name='второй взнос', blank=True, null=True)
    pre_pay_type = models.ForeignKey(
        'TypePay',
        related_name='pre_pay_types',
        on_delete=models.PROTECT,
        verbose_name='тип предоплаты',
        blank=True,
        null=True,
    )
    second_pay_type = models.ForeignKey(
        'TypePay',
        related_name='second_pay_types',
        on_delete=models.PROTECT,
        verbose_name='тип второго платежа',
        blank=True,
        null=True,
    )
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_done = models.DateField(blank=True, null=True)
    date_pre_pay = models.DateField(blank=True, null=True)
    date_second_pay = models.DateField(blank=True, null=True)
    customer = models.ForeignKey(
        'Customer',
        related_name='orders',
        on_delete=models.PROTECT,
        verbose_name='клиент',
        blank=True,
        null=True
    )
    status_order = models.ForeignKey(
        'StatusOrder',
        on_delete=models.PROTECT,
        related_name='orders',
        default=1,
        verbose_name='статус заказа'
    )
    comments = GenericRelation('Comment')
    tasks = GenericRelation('Task')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    def get_my_model_name(self):
        return self._meta.model_name


class TypePay(models.Model):
    type_pay = models.CharField(max_length=150, verbose_name='тип оплаты')

    def __str__(self):
        return self.type_pay


class StatusOrder(models.Model):
    name = models.CharField(max_length=100, verbose_name='наименование')
    start_status = models.BooleanField(verbose_name='начальный статус', default=False)
    finish_status = models.BooleanField(verbose_name='финальный статус', default=False)

    def clean(self):
        if self.start_status:
            start_status = StatusOrder.objects.filter(start_status=True)
            finish_status = StatusOrder.objects.filter(finish_status=True)
            if start_status.exists():
                raise ValidationError(
                    "Может быть только один начальный статус")
            if finish_status.exists():
                raise ValidationError(
                    "Может быть только один финальный статус")

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField(verbose_name='комментарий')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True)
    object_id = models.PositiveIntegerField(blank=True)
    content_object = GenericForeignKey(ct_field='content_type',
                                       fk_field='object_id')
    date = models.DateTimeField(default=datetime.datetime.now, null=True, blank=True)
    staff = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='crm_comment',
        blank=True,
        null=True
    )
    to = models.ForeignKey(
        User,
        verbose_name='Для кого',
        on_delete=models.CASCADE,
        related_name='crm_comment_to',
        blank=True,
        null=True
    )
    is_show = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def get_my_model_name(self):
        return self._meta.model_name


class TypeTask(models.Model):
    type_task = models.CharField(verbose_name='тип задачи', max_length=150)

    def __str__(self):
        return self.type_task


class Task(models.Model):
    task = models.TextField(verbose_name='текст задачи')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True)
    object_id = models.PositiveIntegerField(blank=True)
    content_object = GenericForeignKey(ct_field='content_type',
                                       fk_field='object_id')
    date = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    staff = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='crm_tasks_staff',
        blank=True,
        null=True
    )
    to = models.ForeignKey(
        User,
        verbose_name='Исполнитель',
        on_delete=models.CASCADE,
        related_name='crm_tasks_executor',
        blank=True,
        null=True
    )
    deadline = models.DateTimeField(blank=True, null=True)
    is_done = models.BooleanField(default=False)
    type_task = models.ForeignKey(
        TypeTask,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='tasks',
        verbose_name='тип задачи'
    )
    is_show = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def get_my_model_name(self):
        return self._meta.model_name


class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name='название')
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='заказ покупателя',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

    def get_my_model_name(self):
        return self._meta.model_name


class Measuring(models.Model):
    measuring = models.FileField(
        verbose_name='замер',
        upload_to='measuring/',
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='изделие',
        blank=True,
        null=True,
        related_name='measuring'
    )

    def get_absolute_file_upload_url(self):
        return self.measuring.url


class Project(models.Model):
    project = models.FileField(
        verbose_name='проект',
        upload_to='project/',
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='изделие',
        blank=True,
        null=True,
        related_name='project'
    )

    def get_absolute_file_upload_url(self):
        return self.project.url


class SocialWebCustomers(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='social_web',
        verbose_name='клиент',
        blank=True,
        null=True
    )
    name_social = models.ForeignKey(
        SourceCustomer,
        on_delete=models.CASCADE,
        related_name='social_web',
        verbose_name='название социальной сети',
        blank=True,
        null=True
    )
    id_user = models.CharField(max_length=100, verbose_name='ID')

    def __str__(self):
        return str(self.customer)


class Files(models.Model):
    sheet_id = models.CharField(max_length=150)
    date = models.DateTimeField(auto_now_add=True)
    type_file = models.CharField(max_length=30)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='files',
    )

    class Meta:
        ordering = ['-date']


class Lead(models.Model):
    last_name = models.CharField(max_length=100, verbose_name='фамилия')
    first_name = models.CharField(max_length=100, verbose_name='имя')
    family_name = models.CharField(max_length=100, verbose_name='отчество')
    id_user = models.CharField(max_length=100, verbose_name='ID')
    is_customer = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'
