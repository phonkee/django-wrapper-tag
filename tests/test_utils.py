#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-wrapper-tag
------------

Tests for `django-wrapper-tag` utils module.
"""
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from wrapper_tag import utils


class TestVerifyFuncSignature(TestCase):

    def test_valid_args(self):

        def fn1(tag, argument, data, context):
            pass

        def fn2(tag, argument, data, context, **kwargs):
            pass

        data = [
            [fn1, ['tag', 'argument', 'data', 'context'], {}, True],
            [fn2, ['tag', 'argument', 'data', 'context'], {'need_star_kwargs': True}, True],
        ]

        for item in data:
            message = 'Error fn {}, args: {}, kwargs: {}, expected: {}'.format(item[0], item[1], item[2], item[3])
            try:
                result = utils.verify_func_signature(item[0], *item[1], **item[2])
            except Exception as e:
                self.fail("{}, error: {}".format(message, e))

    def test_invalid_args(self):
        def fn1(tag, argument, data, council):
            pass

        def fn2(tag, argument, data, Conctext):
            pass

        data = [
            [fn1, 'tag', 'argument', 'data', 'context'],
            [fn2, 'tag', 'argument', 'data', 'context'],
        ]

        for item in data:
            self.assertRaises(ImproperlyConfigured, utils.verify_func_signature, *item, exact_names=True)

