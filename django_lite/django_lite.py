# -*- coding:utf-8 -*-

import os, json, inspect, sys
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.db import models
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .services import (
    Config, DBSettings, MiddlewareSettings, ModelFactory,
    StaticSettings, TemplateSettings
)
from .templates import base_apps
from .utils import generate_secret_key


class DjangoLite(object):
    autoconfigure = True
    config = {}
    configuration = None
    _urlpatterns = []
    MODELS = {}

    def __init__(self, file_attr, autoconfigure=True, *args, **kwargs):
        self.base_dir = os.path.dirname(os.path.abspath(file_attr))
        sys.path[0] = os.path.dirname(self.base_dir)
        self.configuration = Config()
        if autoconfigure:
            self.configure()

    def set_url(self):
        self._urlpatterns = [url(r'^admin/', include(admin.site.urls))]

    @property
    def urlpatterns(self):
        from django.contrib.staticfiles.urls import staticfiles_urlpatterns
        return [url(r'^admin/', include(admin.site.urls))] + self._urlpatterns + staticfiles_urlpatterns()

    @property
    def root_urlconf(self):
        return self

    def configure(self, secret_key=None, debug=True, **kwargs):
        if 'override' in kwargs:
            self.config = kwargs.get('overrides')
        else:
            self.configuration.register(DBSettings(self.base_dir))
            self.configuration.register(TemplateSettings(self.base_dir))
            self.configuration.register(MiddlewareSettings())
            self.configuration.register(StaticSettings(self.base_dir))
            self.config['BASE_DIR'] = self.base_dir
            self.config['ROOT_URLCONF'] = self.root_urlconf
            self.config['DEBUG'] = debug
            self.config.update(self.installed_apps())
            self.config.update(self.configuration.settings)
            self.config['SECRET_KEY'] = generate_secret_key() if not secret_key else secret_key
            self.config['SESSION_ENGINE'] = 'django.contrib.sessions.backends.signed_cookies'
        if 'extra' in kwargs:
            self.config.update(kwargs.get('extra'))
        if not settings.configured:
            settings.configure(**self.config)
        import django
        django.setup()

    @property
    def app_label(self):
        base_dir = self.config.get('BASE_DIR')
        if base_dir:
            return os.path.basename(base_dir)

    def new_model(self, *args, **kwargs):
        model = ModelFactory.create(self.app_label, __name__, *args, **kwargs)
        self.MODELS[model.__name__] = model


    def add_view(self, url_pattern, func, name=None):
        params = [url_pattern, func]
        if name is not None:
            params.append(name)
        self._urlpatterns.append(
            url(*params)
        )
        print(self._urlpatterns)

    def installed_apps(self, **kwargs):
        if 'override_apps' in kwargs:
            apps_list = kwargs.get('ovveride_apps')
        else:
            apps_list = base_apps + (
                self.app_label,
            ) + kwargs.get('extra_apps', ())

        return {
            'INSTALLED_APPS': apps_list
        }

    def query(self, model):
        model = self.MODELS.get(model)
        if model:
            return model.objects

    def start(self):
        from django.core.wsgi import get_wsgi_application
        if __name__ == "django_lite.django_lite":
            from django.core.management import execute_from_command_line
            execute_from_command_line(sys.argv)
        else:
            get_wsgi_application()

    def route(self, url_pattern, name=None):
        def wrap(f):
            self.add_view(url_pattern, f, name)
            def wrapped_f(*args):
                f(*args)
            return wrapped_f
        return wrap

    def model(self, admin=True):
        def wrap(cls):
            attributes = inspect.getmembers(cls, lambda attr:not(inspect.isroutine(attr)))
            attrs = dict([attr for attr in attributes if not(attr[0].startswith('__') and attr[0].endswith('__'))])
            self.new_model(
                **{
                    'name': cls.__name__,
                    'admin': admin,
                    'attrs': attrs
                }
            )
            setattr(cls, 'objects', self.query(cls.__name__))
            if hasattr(cls, 'Extra'):
                if hasattr(cls.Extra, 'detail_view'):
                    detail_view = type(cls.__name__ + 'Detail', (DetailView, ), { 'model': self.MODELS[cls.__name__]})
                    self.add_view(cls.Extra.base_url + cls.Extra.detail_view, detail_view.as_view())
                if hasattr(cls.Extra, 'list_view'):
                    list_view = type(cls.__name__ + 'List', (ListView, ), { 'model': self.MODELS[cls.__name__]})
                    self.add_view(cls.Extra.base_url + cls.Extra.list_view, list_view.as_view())
            return cls
        return wrap
