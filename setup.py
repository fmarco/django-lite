import re
import os.path
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__),
                       'django_lite', '__init__.py')) as init_py:
    VERSION = re.search("__version__ = '([^']+)'", init_py.read()).group(1)


setup(
    name='django-lite',
    version=VERSION,
    url='https://github.com/fmarco/django-lite',
    license='MIT',
    author='fmarco',
    author_email='federighi.marco@gmail.com',
    description='A light version of Django.',
    packages=['django_lite'],
    zip_safe=False,
    platforms=['OS Independent'],
    install_requires=[
        'django'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)