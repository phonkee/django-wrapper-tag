=============================
wrapper_tag
=============================

.. image:: https://badge.fury.io/py/wrapper_tag.svg
    :target: https://badge.fury.io/py/wrapper_tag

.. image:: https://travis-ci.org/phonkee/wrapper_tag.svg?branch=master
    :target: https://travis-ci.org/phonkee/wrapper_tag

.. image:: https://codecov.io/gh/phonkee/wrapper_tag/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/phonkee/wrapper_tag

Your project description goes here

Documentation
-------------

The full documentation is at https://wrapper_tag.readthedocs.io.

Quickstart
----------

Install wrapper_tag::

    pip install wrapper_tag

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'wrapper_tag.apps.WrapperTagConfig',
        ...
    )

Add wrapper_tag's URL patterns:

.. code-block:: python

    from wrapper_tag import urls as wrapper_tag_urls


    urlpatterns = [
        ...
        url(r'^', include(wrapper_tag_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
