# -*- coding:utf-8 -*-

db_tpl = """{{
    "DATABASES": {{
                "default": {{
                    "ENGINE": "{0}",
                    "NAME": "{1}"
                }}
            }}
}}
"""

templates_tpl = """
{{
    "TEMPLATES": [
        {{
            "BACKEND": "{0}",
            "DIRS": ["{1}"],
            "APP_DIRS": {2},
            "OPTIONS": {{
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.template.context_processors.tz",
                    "django.contrib.messages.context_processors.messages"
                ]
            }}
        }}
    ]
}}
"""

statics_tpl = """
{{
    "STATIC_URL": "{0}",
    "STATIC_ROOT": "{1}"
}}
"""

base_apps = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles'
)

base_middlewares = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

DEFAULT_DB_ENGINE = 'django.db.backends.sqlite3'
DEFAULT_DB_NAME = 'django_lite'
DEFAULT_TEMPLATE_BACKEND = 'django.template.backends.django.DjangoTemplates'
DEFAULT_APP_DIRS = True
