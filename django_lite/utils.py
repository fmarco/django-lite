# -*- coding:utf-8 -*-
import sys
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string


FIELD_PROXIES = {
    'bigint': 'BigIntegerField',
    'bin': 'BinaryField',
    'boolean': 'BooleanField',
    'char': 'CharField',
    'csv': 'CommaSeparatedIntegerField',
    'date': 'DateField',
    'datetime': 'DateTimeField',
    'decimal': 'DecimalField',
    'duration': 'DurationField',
    'email': 'EmailField',
    'filepath': 'FilePathField',
    'float': 'FloatField',
    'ip': 'GenericIPAddressField',
    'integer': 'IntegerField',
    'nullbool': 'NullBooleanField',
    'slug': 'SlugField',
    'smallint': 'SmallIntegerField',
    'text': 'TextField',
    'time': 'TimeField',
    'url': 'URLField', 
    'uuid': 'UUIDField',
    'fk': 'ForeignKey',
    'm2m': 'ManyToManyField',
    '1to1': 'OneToOneField'
}

DJANGO_FIELDS = FIELD_PROXIES.values()

def generate_secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)


def get_fieldclass_by_name(name):
    field_class_name = FIELD_PROXIES.get(name)
    if field_class_name is None:
        raise Exception('Field Class not found!')
    field_class = getattr(models, field_class_name)
    return field_class


class FieldStub(object):
    def __call__(self, *args, **kwargs):
        return get_fieldclass_by_name(self.__class__.__name__)(*args, **kwargs)


for proxy_name in FIELD_PROXIES.keys():
    setattr(sys.modules[__name__], proxy_name ,type(proxy_name, (FieldStub,), {})())


def generate_get_absolute_url(prefix):
    def get_absolute_url(self):
            return reverse('{0}-detail'.format(prefix), kwargs={'pk': self.pk})
    return get_absolute_url
