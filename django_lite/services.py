# -*- coding:utf-8 -*-
import json
import os
from django.contrib import admin
from django.db import models

from .templates import *
from .utils import get_fieldclass_by_name


class BaseSettings(object):

    def template(self, *args):
        settings_str = self.tpl.format(*args)
        return json.loads(settings_str)

    @property
    def to_settings(self):
        raise NotImplementedError(
            'You should implement the tojson method'
        )


class DBSettings(BaseSettings):
    engine = ''
    name = ''
    tpl = db_tpl

    def __init__(self, base_dir, *args, **kwargs):
        super(DBSettings, self).__init__(*args, **kwargs)
        self.base_dir = base_dir
        self.engine = kwargs.get('db_engine', DEFAULT_DB_ENGINE)
        self.name = os.path.join(
            self.base_dir,
            kwargs.get('db_name', DEFAULT_DB_NAME)
        )

    @property
    def to_settings(self):
        return self.template(self.engine, self.name)


class TemplateSettings(BaseSettings):

    backend = ''
    app_dirs = True
    base_dir = ''
    tpl = templates_tpl

    def __init__(self, base_dir, *args, **kwargs):
        super(TemplateSettings, self).__init__(*args, **kwargs)
        self.backend = kwargs.get('backend', DEFAULT_TEMPLATE_BACKEND)
        self.app_dirs = kwargs.get('app_dirs', DEFAULT_APP_DIRS)
        self.base_dir = base_dir

    @property
    def to_settings(self):
        return self.template(self.backend, self.base_dir, str(self.app_dirs).lower())


class MiddlewareSettings(BaseSettings):
    def __init__(self, *args, **kwargs):
        super(MiddlewareSettings, self).__init__(*args, **kwargs)

    @property
    def to_settings(self):

        return {
            'MIDDLEWARE_CLASSES': base_middlewares
        }


class StaticSettings(BaseSettings):

    tpl = statics_tpl

    def __init__(self, base_dir, *args, **kwargs):
        super(StaticSettings, self).__init__(*args, **kwargs)
        self.base_dir = base_dir

    @property
    def to_settings(self):
        return self.template('/static/', os.path.join(self.base_dir, 'static'))


class ModelFactory(object):

    @classmethod
    def create(cls, app_label, module, *args, **kwargs):
        try:
            name = kwargs.pop('name')
            kwargs['attrs'] = kwargs.pop('attrs', {})
            has_admin = kwargs.pop('admin', False)
            META = type('Meta', (object,), {'app_label': app_label})
            kwargs['attrs']['Meta'] = META
            kwargs['attrs']['__module__'] = module
            fields = kwargs.pop('fields', {})
            for arg, opts in fields.iteritems():
                field_obj = None
                field = fields[arg]
                if isinstance(field, list):
                    field_class = get_fieldclass_by_name(field[0])
                    field_obj = field_class(**field[1])
                elif isinstance(field, dict):
                    field_obj = opts
                kwargs['attrs'][arg] = field_obj
            model = type(name, (models.Model,), kwargs['attrs'])
            if has_admin:
                admin.site.register(model)
            return model
        except KeyError:
            return None


class Config(object):

    _data = []

    def __init__(self, *args, **kwargs):
        pass

    @property
    def settings(self):
        res = {}
        for conf in self._data:
            res.update(conf.to_settings)
        return res

    def register(self, conf):
        self._data.append(conf)
