#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase

from wrapper_tag.rendered import RenderedTag


class TestRenderedTag(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_data(self):
        data = {
            "some": "data"
        }
        tag = "tag"
        content = "content"

        rt = RenderedTag(content, tag, **data)
        for key, value in data.items():
            self.assertEqual(getattr(rt, key), data[key])

        self.assertEqual(getattr(rt, "content"), content)
        self.assertEqual(rt.content, content)
        self.assertEqual(getattr(rt, 'tag'), tag)
        self.assertEqual(getattr(rt, 'some'), "data")

        self.assertEqual(str(rt), content)
        self.assertEqual(repr(rt), content)
