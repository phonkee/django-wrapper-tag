=============================
wrapper_tag
=============================

.. image:: https://badge.fury.io/py/django-wrapper-tag.png
    :target: https://badge.fury.io/py/django-wrapper-tag

Wrapping template tag for django

Documentation
-------------

Wrapper tag provides base class for wrapping tag. Wrapping tag which can have defined keyword arguments, keyword
arguments group in declarative way, and provide multiple steps of template rendering.

Example::

    from django import template
    register = template.Library()

    @wrapper_tag.register_tag(register)
    class ExampleTag(wrapper_tag.Tag):

        title = wrapper_tag.Keyword(help_text=('title for example tag'))

        class Meta:
            template = "<div{{ title__rendered }}>{{ content }}</div>"

        def render_title(self, argument, data, context):
            if argument.name not in data:
                return
            return ' title="{title}"'.format(data[argument.name])

And then simply use tag in template::

    {% example title="Some informational title" %}
        Content
    {% end:example %}

This will yield to::

    <div title="Some informational title">
        Content
    </div>

That was just a simple eample what wrapper tag can do. It can do much more than that.

Quickstart
----------

Install wrapper_tag::

    pip install django-wrapper-tag

Then use it in a project::

    INSTALLED_APPS = (
        'wrapper_tag',
    )

Features
--------

Wrapper tag provides multiple features for tag and arguments.

* Automatically generates documantation about arguments to tag documentation
* Define tag aliases and automatically register them as tags.
* Provide custom render method for tag (`render_tag`)
* when `TEMPLATE_DEBUG` is enabled wrapper tag runs validations for callbacks

Tag arguments features:

* default values for arguments
* choices for arguments
* validators for arguments

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ python runtests.py

Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
