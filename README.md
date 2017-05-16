django-lite
===============

A simple lightweight version of Django

Why?
--------

To make simple setup little web app or testing or simply to make some experiments with the framework.


Quickstart
--------

    from django_lite.django_lite import DjangoLite

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