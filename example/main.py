# -*- coding:utf-8 -*-
from django_lite.django_lite import DjangoLite
from django_lite.utils import bigint, char, fk, m2m

app = DjangoLite(__file__)


@app.model()
class M1(object):
    x = bigint(max_length=10)
    y = char(max_length=255)
    z = fk('M2')

    class Extra:
        base_url = r'^m1/'
        detail_view = r'in_detail/(?P<pk>\d+)/$'
        list_view = r'listing$'
        create_view = r'create$'
        delete_view = r'destroy/(?P<pk>\d+)/$'
        update_view = r'update/(?P<pk>\d+)/$'


@app.model()
class M2(object):
    x = bigint(max_length=10)


@app.model()
class M3(object):
    many = m2m('M1')

from django.shortcuts import render


@app.route(r'^test$')
def test_view(request):
    return render(
        request,
        'index.html',
        {
            'objects': M1.objects.all()
        }
    )


if __name__ == '__main__':
    app.start()
