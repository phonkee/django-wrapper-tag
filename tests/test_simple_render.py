#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-wrapper-tag
------------

Tests for `django-wrapper-tag` simple render.
"""
from __future__ import absolute_import, print_function, unicode_literals
from django import template
from django.test import TestCase

from wrapper_tag import arguments, tag


class TestSimpleRender(TestCase):

    def test_simple_render(self):

        data = [
            {
                'template': '{% test title="value" on_click="alert" %} '
                            'text'
                            '{% test title="value2" name="myname" %}'
                            'next text'
                            '{% test title="value3" %}'
                            'this is nodelist'
                            '{% end:test %}'
                            '{% end:test %}'
                            '{% end:test %}',
            }
        ]

        for item in data:
            t = template.Template('{% load wrapper_tag_test_tags %}' + item['template'])
            t.render({})


class TestArgumentClean(TestCase):

    def test_argument_clean(self):

        class TestTag(tag.Tag):
            title = arguments.Keyword()

        self.assertTrue('render_title' in dir(TestTag))
        self.assertTrue(callable(TestTag.render_title))
