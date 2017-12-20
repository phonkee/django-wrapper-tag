#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template import TemplateDoesNotExist
from django.test import TestCase

from wrapper_tag import Options


class TestOptions(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_options_start_tag(self):
        class Meta:
            pass

        class Meta2:
            start_tag = "starter"

        self.assertEqual(Options(Meta, "CustomTag").start_tag, "custom")
        self.assertEqual(Options(Meta2, "CustomTag").start_tag, Meta2.start_tag)
        self.assertEqual(Options(Meta, "CustomTa").start_tag, "custom_ta")

    def test_options_end_tag(self):
        class Meta:
            pass

        class Meta2:
            start_tag = "starter"

        class Meta3:
            start_tag = "starter"
            end_tag = "starter:over"

        self.assertEqual(Options(Meta, "CustomTag").end_tag, "end:custom")
        self.assertEqual(Options(Meta2, "CustomTag").end_tag, "end:starter")
        self.assertEqual(Options(Meta3, "CustomTag").end_tag, "starter:over")

    def test_options_namespace(self):
        class Meta:
            pass

        class Meta2:
            namespace = "wrapwrap"

        self.assertEqual(Options(Meta, "CustomTag").namespace, None)
        self.assertEqual(Options(Meta2, "CustomTag").namespace, Meta2.namespace)
        self.assertEqual(Options(Meta2, "CustomTag").start_tag, "wrapwrap:custom")
        self.assertEqual(Options(Meta2, "CustomTag").end_tag, "end:wrapwrap:custom")

    def test_options_as_var_only(self):
        class Meta:
            pass

        class Meta2:
            as_var_only = True

        self.assertEqual(Options(Meta, "CustomTag").as_var_only, False)
        self.assertEqual(Options(Meta2, "CustomTag").as_var_only, True)

    def test_template(self):
        class Meta:
            template = "templ"

        self.assertEqual(Options(Meta, "Tag").template, Meta.template)

    def test_template_name(self):
        class Meta:
            template_name = "existing.html"

        # this raises error, we need to find out how to set templates directory correctly
        with self.assertRaises(TemplateDoesNotExist):
            Options(Meta, "Tag").get_template()

    def test_no_template(self):
        class Meta:
            pass

        with self.assertRaises(TemplateDoesNotExist):
            Options(Meta, "Tag").get_template()



