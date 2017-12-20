#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

from django.test import TestCase

from wrapper_tag import globstr


class TestGlobStr(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_quote(self):
        data = [
            ["hello_<int>", "^hello_\d+$"],
            ["hello_<str>", "^hello_[a-zA-Z]+$"],
            ["hello_<ident>", "^hello_[a-zA-Z]{1}[a-zA-Z_\-0-9]+$"],
        ]

        # clear cache first
        globstr.clear()

        for item in data:
            self.assertEqual(globstr._quote(item[0]), item[1])

    def test_get(self):
        data = [
            "hello_<int>",
            "hello_<str>",
            "hello_<ident>",
        ]

        # clear cache first
        globstr.clear()

        for i, item in enumerate(data, 1):
            for j in range(random.randint(2, 10)):
                globstr.get(item)
                self.assertEqual(len(globstr.__cache__), i)
