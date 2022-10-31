from datetime import datetime

from django import template

register = template.Library()


@register.filter
def addclass(field):
    return datetime.utcfromtimestamp(field).strftime('%Y-%m-%d %H:%M:%S')


@register.filter
def unix_to_date(field):
    return datetime.utcfromtimestamp(field).strftime('%Y-%m-%d %H:%M:%S')


@register.filter
def cal_date(field):
    return field


@register.filter
def len_list(arr):
    return len(arr)
