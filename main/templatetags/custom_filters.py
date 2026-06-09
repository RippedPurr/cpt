from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def days_until(value):
    if not value:
        return None
    delta = value - timezone.now()
    return delta.days


from django import template

register = template.Library()


@register.filter
def ru_plural(value, variants):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return variants.split(',')[2]

    variants_list = variants.split(',')

    if value % 10 == 1 and value % 100 != 11:
        return variants_list[0]
    elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
        return variants_list[1]
    else:
        return variants_list[2]