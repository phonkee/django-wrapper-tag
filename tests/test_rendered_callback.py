#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-wrapper-tag
------------

Tests for `django-wrapper-tag` rendered_callback.
"""
from __future__ import absolute_import, print_function, unicode_literals

from django.template import Context, Template
from django.test import TestCase


class TestRenderedCallback(TestCase):

    def test_callback(self):

        template = """{% load events %}
        {% ex_rendered on_click="asdf" as tmp %}
            hello
        {% end:ex_rendered %}
        {{ tmp.events.on_click }}
        """
        rendered = Template(template).render(Context())
        self.assertEquals(rendered.strip(), 'asdf')
