#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = re.search(
    "__version__[\s]*=[\s]*(.*)[\s]*",
    open('wrapper_tag/__init__.py').read()).group(1).strip('"\'')

if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (__version__, __version__))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-wrapper-tag',
    version=__version__,
    description="""Wrapping template tag for django""",
    long_description=readme + '\n\n' + history,
    author='Peter Vrba',
    author_email='phonkee@phonkee.eu',
    url='https://github.com/phonkee/django-wrapper-tag',
    packages=[
        'wrapper_tag'
    ],
    include_package_data=True,
    install_requires=[
        'django>=1.8',
        'six',
    ],
    license="MIT",
    zip_safe=False,
    keywords='django-wrapper-tag',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
