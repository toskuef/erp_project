# Generated by Django 3.2.15 on 2022-09-12 13:29

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_title', models.CharField(max_length=100, verbose_name='назавние области')),
            ],
            options={
                'verbose_name': 'область',
                'verbose_name_plural': 'области',
            },
        ),
        migrations.CreateModel(
            name='AddressCountry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_title', models.CharField(max_length=100, verbose_name='назавние страны')),
            ],
            options={
                'verbose_name': 'страна',
                'verbose_name_plural': 'страны',
            },
        ),
        migrations.CreateModel(
            name='AddressRegion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region_title', models.CharField(max_length=100, verbose_name='название района')),
            ],
            options={
                'verbose_name': 'район',
                'verbose_name_plural': 'районы',
            },
        ),
        migrations.CreateModel(
            name='AddressStreet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_title', models.CharField(max_length=100, verbose_name='название улицы')),
            ],
            options={
                'verbose_name': 'улица',
                'verbose_name_plural': 'улицы',
            },
        ),
        migrations.CreateModel(
            name='AddressTown',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('town_title', models.CharField(max_length=100, verbose_name='название города')),
            ],
            options={
                'verbose_name': 'город',
                'verbose_name_plural': 'города',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=100, verbose_name='фамилия')),
                ('first_name', models.CharField(max_length=100, verbose_name='имя')),
                ('family_name', models.CharField(max_length=100, verbose_name='отчество')),
                ('phone', models.CharField(max_length=15, verbose_name='номер телефона')),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='дата создания')),
                ('is_show', models.BooleanField(default=False)),
                ('creater_customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customers', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name': 'клиент',
                'verbose_name_plural': 'клиенты',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='название')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='сумма заказа')),
                ('pre_pay', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='предоплата')),
                ('second_pay', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='второй взнос')),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_done', models.DateField(blank=True, null=True)),
                ('date_pre_pay', models.DateField(blank=True, null=True)),
                ('date_second_pay', models.DateField(blank=True, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='crm.customer', verbose_name='клиент')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='название')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='crm.order', verbose_name='заказ покупателя')),
            ],
        ),
        migrations.CreateModel(
            name='SourceCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=15, verbose_name='Источник')),
            ],
        ),
        migrations.CreateModel(
            name='StatusOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='наименование')),
            ],
        ),
        migrations.CreateModel(
            name='TypePay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_pay', models.CharField(max_length=150, verbose_name='тип оплаты')),
            ],
        ),
        migrations.CreateModel(
            name='TypeTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_task', models.CharField(max_length=150, verbose_name='тип задачи')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.TextField(verbose_name='текст задачи')),
                ('object_id', models.PositiveIntegerField(blank=True)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now, null=True)),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('is_done', models.BooleanField(default=False)),
                ('is_show', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='crm_tasks_staff', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='crm_tasks_executor', to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель')),
                ('type_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tasks', to='crm.typetask', verbose_name='тип задачи')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='SocialWebCustomers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_user', models.CharField(max_length=100, verbose_name='ID')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='social_web', to='crm.customer', verbose_name='клиент')),
                ('name_social', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='social_web', to='crm.sourcecustomer', verbose_name='название социальной сети')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.FileField(blank=True, upload_to='project/', verbose_name='проект')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project', to='crm.product', verbose_name='изделие')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='pre_pay_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='pre_pay_types', to='crm.typepay', verbose_name='тип предоплаты'),
        ),
        migrations.AddField(
            model_name='order',
            name='second_pay_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='second_pay_types', to='crm.typepay', verbose_name='тип второго платежа'),
        ),
        migrations.AddField(
            model_name='order',
            name='status_order',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='crm.statusorder', verbose_name='статус заказа'),
        ),
        migrations.CreateModel(
            name='Measuring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measuring', models.FileField(blank=True, upload_to='measuring/', verbose_name='замер')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='measuring', to='crm.product', verbose_name='изделие')),
            ],
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sheet_id', models.CharField(max_length=150)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('type_file', models.CharField(max_length=30)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='crm.product')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers', to='crm.sourcecustomer', verbose_name='Источник'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='комментарий')),
                ('object_id', models.PositiveIntegerField(blank=True)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now, null=True)),
                ('is_show', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='crm_comment', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='crm_comment_to', to=settings.AUTH_USER_MODEL, verbose_name='Для кого')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_house', models.IntegerField(blank=True, verbose_name='номер дома')),
                ('num_housing', models.IntegerField(blank=True, verbose_name='номер корпуса')),
                ('num_door', models.IntegerField(blank=True, verbose_name='номер подъезда')),
                ('num_level', models.IntegerField(blank=True, verbose_name='номер этажа')),
                ('num_flat', models.IntegerField(blank=True, verbose_name='номер квартиры')),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='addresses', to='crm.addressarea', verbose_name='область')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='addresses', to='crm.addresscountry', verbose_name='страна')),
                ('customer', models.ManyToManyField(blank=True, related_name='addresses', to='crm.Customer', verbose_name='клиенты')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='addresses', to='crm.addressregion', verbose_name='район')),
                ('street', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='addresses', to='crm.addressstreet', verbose_name='улица')),
                ('town', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='addresses', to='crm.addresstown', verbose_name='город')),
            ],
            options={
                'verbose_name': 'адрес',
                'verbose_name_plural': 'адреса',
            },
        ),
    ]
