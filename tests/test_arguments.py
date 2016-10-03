#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-wrapper-tag
------------

Tests for `django-wrapper-tag` simple render.
"""
from __future__ import absolute_import, print_function, unicode_literals
from django.test import TestCase

import wrapper_tag


class TestArgument(TestCase):

    def test_argument_clean(self):

        class ExampleTag(wrapper_tag.Tag):
            title = wrapper_tag.Keyword()



