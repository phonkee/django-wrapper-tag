#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import uuid

from django.template.base import TemplateSyntaxError
from django.test import TestCase

from wrapper_tag import Positional, Keyword, KeywordGroup


class TestPositionalArgument(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_positional_simple(self):
        pa = Positional()
        args = [1, ]
        pa.claim_arguments(args, {})
        self.assertEqual(len(args), 0)

    def test_positional_simple_invalid(self):

        test_data = [
            [],
        ]

        for item in test_data:
            pa = Positional(name="pa")
            with self.assertRaises(TemplateSyntaxError):
                args, _ = pa.claim_arguments(item, {})

    def test_positional_is_varargs(self):
        test_data = [
            [1, 2, 3, 4, 5, 6, 7, 8],
            [1, 2],
            [],
        ]

        for item in test_data:
            pa = Positional(is_varargs=True)

            copied = copy.deepcopy(item)

            got = pa.claim_arguments(item, {})
            self.assertEqual(len(item), 0)
            self.assertEqual(copied, got)


class TestKeywordArgument(TestCase):

    def test_keyword_simple(self):
        """
        test simple keyword
        :return:
        """
        kwargs = {"pa": 1}
        value = Keyword(name="pa").claim_arguments([], kwargs)
        self.assertEqual(value, 1)
        self.assertDictEqual(kwargs, {})

    def test_keyword_bulk(self):
        """
        Test whether all keys from kwargs are claimed
        :return:
        """
        kwargs = {"x" + str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()) for x in range(100)}

        for k in list(kwargs.keys()):
            Keyword(name=k).claim_arguments([], kwargs)

        self.assertEqual(len(kwargs), 0)


class TestKeywordGroupArgument(TestCase):

    def test_single_pattern(self):
        data = [
            ["test_<int>", {"test_1": 2, "test_2": 123, "test_01234": "value"}],
            ["test_<str>", {"test_a": 2, "test_asdg": 123, "test_bfadfbas": "value"}],
        ]

        for item in data:
            pattern, kwargs = item
            KeywordGroup(pattern).claim_arguments([], kwargs)
            self.assertEqual(len(kwargs), 0)

    def test_single_pattern_invalid(self):
        data = [
            ["test_<int>", {"test_a": 2, "test_v": 123, "test_asdfsf_": "value"}],
            ["test_<ident>", {"test_0": 2, "test_0123": 123, "test_23something": "value"}],
        ]

        for item in data:
            pattern, kwargs = item
            expect = len(kwargs)
            KeywordGroup(pattern).claim_arguments([], kwargs)
            self.assertEqual(len(kwargs), expect)

    def test_invalid_patterns(self):
        data = [
            123,
            None,
            1.2,
        ]

        for pattern in data:
            with self.assertRaises(TemplateSyntaxError):
                KeywordGroup(pattern)
