#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-wrapper-tag
------------

Tests for `django-wrapper-tag` docgen.
"""
from __future__ import absolute_import, print_function, unicode_literals
from django.test import TestCase

import wrapper_tag
from wrapper_tag import docgen


class TestDocgen(TestCase):

    def test_docgen(self):

        class ExampleTag(wrapper_tag.Tag):
            """
            Example tag gives possibility to do things.

            Example::

                {% example %}
                    Hello world!
                {% end:example %}

            {arguments}

            """
            title = wrapper_tag.Keyword()
            name = wrapper_tag.Keyword()

            on_click = wrapper_tag.Event()

            open = wrapper_tag.Method()

        generated = docgen.generate(ExampleTag)
        print(generated)
