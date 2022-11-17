from datetime import datetime

from django import template

from users.models import AnySettingsUser

register = template.Library()


@register.filter
def addclass(field):
    return datetime.utcfromtimestamp(field).strftime('%Y-%m-%d %H:%M:%S')


@register.filter(name='add_id')
def add_id(value, arg):
    return value.as_widget(attrs={'id': arg})


@register.filter
def unix_to_date(field):
    return datetime.utcfromtimestamp(field).strftime('%Y-%m-%d %H:%M:%S')


@register.filter
def cal_date(field):
    return field


@register.filter
def len_list(arr):
    return len(arr)
