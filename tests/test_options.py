#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-wrapper-tag
------------

Tests for `django-wrapper-tag` models module.
"""

from django.test import TestCase

from wrapper_tag import tag


class TestOptionsTag(TestCase):

    def test_auto_start_end_tag(self):
        class CustomTag(tag.Tag):
            pass
        self.assertEqual(CustomTag.options.start_tag, 'custom', 'start_tag failed')
        self.assertEqual(CustomTag.options.end_tag, 'end:custom', 'end_tag failed')

    def test_auto_end_tag(self):
        class CustomTag(tag.Tag):
            class Meta:
                start_tag = "nice"

    def test_custom_start_end(self):
        class CustomTag(tag.Tag):
            class Meta:
                start_tag = "nice"
                end_tag = "hack"
        self.assertEqual(CustomTag.options.start_tag, 'nice', 'start_tag failed')
        self.assertEqual(CustomTag.options.end_tag, 'hack', 'end_tag failed')

