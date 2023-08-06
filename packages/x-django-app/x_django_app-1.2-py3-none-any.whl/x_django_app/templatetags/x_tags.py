# x-django-app templatetags
from django import template
from langdetect import detect
import json
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db.models import Sum


register = template.Library()


@register.filter
def class_name(item):
    '''
    Return the class name of the item
    '''
    return item.__class__.__name__


@register.filter
def detect_language(item):
    '''
    Detect the text langugage
    '''
    try:
        language = str(item)
    except Exception:
        language = 'an error in the given string'

    # get language code
    detection = detect(language)
    # check if language detected is farise of urdu
    if detection == 'ur' or detection == 'fa':
        # replace it with arabic one
        detection = 'ar'
    return detection


@register.filter
def get_data(text, key):
    '''
    Return data in the textfield
    '''
    data = dict(json.loads(text.replace("'", '"')))
    try:
        return data[key]
    except Exception:
        return


@register.filter
def to_string(number):
    '''
    Convert number to string
    '''
    return str(number)


@register.simple_tag
def add_parameter(link, parameter, variable):
    '''
    Add parameter to link
    '''
    if link[-1] == '/':
        return f"{link}?{parameter}{variable}"
    else:
        first_split = link.split('?')
        if "&" in first_split[1]:
            second_split = first_split[1].split('&')
        else:
            second_split = [first_split[1]]
        new_link = first_split[0]
        if len(second_split) > 1:
            if parameter in second_split[0]:
                new_link = f"{new_link}?{parameter}{variable}"
            else:
                new_link = f"{new_link}?{second_split[0]}"
            second_split.pop(0)
            for item in second_split:
                if parameter in item:
                    new_link = f"{new_link}&{parameter}{variable}"
                else:
                    new_link = f"{new_link}&{item}"
            if f"{parameter}{variable}" not in new_link:
                new_link = f"{new_link}&{parameter}{variable}"
        else:
            if parameter in second_split[0]:
                new_link = f"{new_link}?{parameter}{variable}"
            else:
                new_link = "{0}?{1}&{2}{3}".format(
                                                new_link,
                                                second_split[0],
                                                parameter,
                                                variable)
        return new_link


@register.simple_tag(takes_context=True)
def x_sort(context, active, target):
    '''
    sort function template tag
    '''
    request = context['request']
    if active == target:
        target = f"-{target}"

    new_link = add_parameter(request.get_full_path(), 'sort=', target)

    return new_link


@register.filter
def trunc(text, digits=128):
    '''
    Return the class name of the item
    '''
    if text:
        digits = int(digits)
        trancated = (text[:digits] + '..') if len(text) > digits else text
    else:
        trancated = text

    return trancated


@register.filter
def make_clear(text):
    '''
    return text with uppercase and without '_'
    '''
    text = text.replace('_', ' ')
    text = f'{text[0].upper()}{text[1:]}'
    return text


@register.simple_tag
def get_sum(results_objects, field_name):
    '''
    Return the sum of given objects
    '''
    field_sum = f"{field_name}__sum"

    if results_objects.all():
        results_total = float(results_objects.aggregate(
                                            Sum(field_name)).get(field_sum))
    else:
        return 0

    return results_total


@register.simple_tag
def permission_check(user, permission):
    '''
    Check if user has permission
    '''
    try:
        content_type = ContentType.objects.filter(app_label=permission.split('.')[0])
        user_permission = Permission.objects.get(
                                            content_type__in=content_type,
                                            codename=permission.split('.')[1])
        if user.user_permissions.filter(
                                    id=user_permission.id).exists():
            return True
        else:
            return False
    except Exception as error_type:
        print(f"{permission}-{error_type}")
        return False
