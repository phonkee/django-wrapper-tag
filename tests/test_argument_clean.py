#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-wrapper-tag
------------

Tests for `django-wrapper-tag` simple render.
"""
from __future__ import absolute_import, print_function, unicode_literals
from django.test import TestCase

from wrapper_tag import arguments
from wrapper_tag import tag


class TestArgumentClean(TestCase):

    def test_argument_clean(self):
        class TestTag(tag.Tag):
            title = arguments.Keyword()

        self.assertTrue('clean_title' in dir(TestTag) and callable(TestTag.clean_title))
