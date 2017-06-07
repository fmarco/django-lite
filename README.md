django-lite
===============
[![PyPI](https://img.shields.io/pypi/pyversions/django-lite.svg)](https://pypi.python.org/pypi/django-lite/)
[![PyPI](https://img.shields.io/pypi/l/django-lite.svg)](https://pypi.python.org/pypi/django-lite/)
[![Latest Version](https://img.shields.io/pypi/v/django-lite.svg)](https://pypi.python.org/pypi/django-lite/)
[![PyPI](https://img.shields.io/pypi/dm/django-lite.svg)](https://pypi.python.org/pypi/django-lite/)

A simple lightweight version of Django

Why?
--------

To make simple setup little web app or testing or simply to make some experiments with the framework.


Installation
--------

    pip install django-lite


Quickstart
--------

    from django_lite.django_lite import DjangoLite
    from django_lite.utils char

    app = DjangoLite(__file__)

    @app.model()
    class Sample(object):
        some_field = char(max_length=255)

        class Extra:
            base_url = r'^sample/'
            detail_view = r'detail/(?P<pk>\d+)/$'
            list_view = r'list/$'

    if __name__ == '__main__':
        app.start()


Or explore 'example' folder!


Commands
--------

    python path/to/file.py make_models ( > dest_file.py )

    python path/to/file.py make_views ( > dest_file.py )

    python path/to/file.py make_urls ( > dest_file.py )

    python path/to/file.py make_settings ( > dest_file.py )


Tested versions
--------

python 2.7 - django 1.11


TODOS
--------

* Add useful commands
* Add some tests
* Some refactoring
...

Feel free to contribute!