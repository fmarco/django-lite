# -*- coding:utf-8 -*-

import os, json, inspect, sys
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.db import models
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .services import (
    Config, DBSettings, MiddlewareSettings, ModelFactory,
    StaticSettings, TemplateSettings
)
from .templates import base_apps
from .utils import generate_secret_key, generate_get_absolute_url, DJANGO_FIELDS


separator = '    '
header = '# -*- coding:utf-8 -*-'


DJ_CLASSES = [ CreateView, DeleteView, DetailView, ListView, UpdateView ]

DJ_CLASSES_IMPORT = {
    'CreateView': 'from django.views.generic.edit import CreateView',
    'UpdateView': 'from django.views.generic.edit import UpdateView',
    'DeleteView': 'from django.views.generic.edit import DeleteView',
    'DetailView': 'from django.views.generic.detail import DetailView',
    'ListView': 'from django.views.generic.list import ListView'
}


class DjangoLite(object):

    extra_mapping = {
        'detail_view': ('Detail', DetailView, False),
        'list_view': ('List', ListView, False),
        'create_view': ('Create', CreateView, True),
        'delete_view': ('Delete', DeleteView, False),
        'update_view': ('Update', UpdateView, True)
    }

    commands = {
        'make_models': 'generate_models',
        'make_urls': 'generate_urls',
        'make_views': 'generate_views',
        'make_settings': 'generate_settings'
    }

    autoconfigure = True
    config = {}
    configuration = None
    _urlpatterns = []
    MODELS = {}
    VIEWS = {}

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
        setattr(model, 'get_absolute_url', generate_get_absolute_url(model.__name__.lower()))
        self.MODELS[model.__name__] = model

    def add_view(self, url_pattern, func, name=None):
        params = [url_pattern, func]
        if name is None:
            name = func.__name__
        self._urlpatterns.append(
            url(*params, name=name)
        )
        self.VIEWS[func.__name__] = func

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
            try:
                command = sys.argv[1]
                if command in self.commands.keys():
                    cmd = getattr(self, self.commands.get(command))
                    for line in cmd():
                        sys.stdout.write("%s\n" % line)
                    return
            except IndexError:
                pass
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

    def generate_view(self, cls, view_name):
        try:
            view_name, view_parent, edit = self.extra_mapping[view_name]
            cls_name = cls.__name__
            view_class_name =  '{0}{1}'.format(cls_name, view_name)
            data = { 'model': self.MODELS[cls_name]}
            if edit:
                data['fields'] = '__all__'
            return type(view_class_name, (view_parent, ), data)
        except KeyError:
            pass

    def model(self, admin=True, crud=False):
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
            generated_views = []
            if hasattr(cls, 'Extra'):
                base_url = ''
                if hasattr(cls.Extra, 'base_url'):
                    base_url = cls.Extra.base_url
                else:
                    base_url = cls.__name__.lower()
                for extra in cls.Extra.__dict__.iteritems():
                    view = self.generate_view(cls, extra[0])
                    if view is not None:
                        generated_views.append(extra[0])
                        view_name = '{0}_{1}'.format(cls.__name__.lower(), extra[0])
                        url = '{0}{1}'.format(base_url, extra[1])
                        self.add_view(url, view.as_view(), view_name)
            else:
                base_url = cls.__name__.lower()
            if crud:
                crud_views = set(self.extra_mapping.keys())
                remaining = crud_views - set(generated_views)
                for new_view in remaining:
                    view = self.generate_view(cls, new_view)
                    view_name = '{0}_{1}'.format(cls.__name__.lower(), new_view)
                    view_info = self.extra_mapping[new_view]
                    url_suffix = view_info[0].lower()
                    url = '^{0}/{1}'.format(base_url, url_suffix)
                    if view_info[2] or new_view == 'delete_view':
                        url = '{0}/{1}$'.format(url, '(?P<pk>\d+)')
                    self.add_view(url, view.as_view(), view_name)
            return cls
        return wrap

    def generate_models(self):
        yield header
        yield 'from django.db import models'
        yield 'from django.utils.translation import ugettext_lazy as _\n'
        for k, v in self.MODELS.iteritems():
            yield 'class {0}(models.Model):'.format(k)
            fields = v._meta.get_fields()
            for field in fields:
                if field.__class__.__name__ in DJANGO_FIELDS:
                    yield '{0}{1} = models.{2}()'.format(separator, field.name, field.__class__.__name__)
            yield '\n{0}class Meta:'.format(separator)
            yield '{0}{1}verbose_name = _(\'{2}\')'.format(separator, separator, k.lower())
            yield '{0}{1}verbose_name_plural = _(\'{2}s\')'.format(separator, separator, k.lower())
            yield '\n{0}def __str__(self):'.format(separator)
            yield '{0}{1}return self.pk'.format(separator, separator)
            yield '\n'

    def generate_urls(self):
        from django.core.urlresolvers import RegexURLResolver
        patterns = []
        for url in self.urlpatterns:
            if isinstance(url, RegexURLResolver):
                if url.app_name == 'admin':
                    str_pattern = '{0}url(r\'^admin/\', include(admin.site.urls)),'.format(separator)
                    patterns.append(str_pattern)
            else:
                if 'static' not in url.regex.pattern:
                    str_pattern = '{0}url(r\'{1}\', views.{2}),'.format(separator, url.regex.pattern, url.callback.__name__)
                    patterns.append(str_pattern)
        yield header
        yield 'from django.conf.urls import url'
        yield 'from django.contrib.staticfiles.urls import staticfiles_urlpatterns'
        yield ''
        yield 'from . import views\n'
        yield 'urlpatterns = ['
        for url in patterns:
            yield url
        yield '] + staticfiles_urlpatterns()\n'

    def generate_views(self):
        yield header
        declarations = []
        counters = {}
        for k, f in self.VIEWS.iteritems():
            if hasattr(f, 'view_class'):
                cls = f.view_class
                cls_str = ''
                for dj_class in DJ_CLASSES:
                    if issubclass(cls, dj_class):
                        dj_class_name = dj_class.__name__
                        try:
                            counters[dj_class_name] += 1
                        except KeyError:
                            counters[dj_class_name] = 1
                        cls_str = 'class {0}({1}):'.format(cls.__name__, dj_class.__name__)
                        cls_str += '\n{0}model={1}'.format(separator, cls.model.__name__)
                        declarations.append(cls_str)
            else:
                declarations.append(inspect.getsource(f))
        for import_str, count in counters.iteritems():
            if count > 0:
                yield DJ_CLASSES_IMPORT[import_str]
        for declaration in declarations:
            yield '\n'
            yield declaration

    def generate_settings(self):
        yield header
        for k, v in settings._wrapped.__dict__.iteritems():
            try:
                yield '{0} = {1}'.format(k, json.dumps(settings._wrapped.__dict__[k]))
            except TypeError:
                pass
