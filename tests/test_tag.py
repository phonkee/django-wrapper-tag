# !/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.template import Engine, Context
from django.test import TestCase

from tests.templatetags import arguments_tags
from wrapper_tag import KeywordGroup, Keyword, Positional, Tag, register_tag
from .templatetags import compile_tags


class TestTags(TestCase):

    @classmethod
    def setUp(cls):
        cls.engine = Engine(debug=True, libraries={
            "compile_tags": "tests.templatetags.compile_tags",
            "arguments_tags": "tests.templatetags.arguments_tags",
        })

        # reference
        _ = compile_tags

        super().setUpClass()

    def tearDown(self):
        pass

    def compile_tag(self, tag_class, template, tag_lib="compile_tags"):
        """
        compile_tag compiles template and returns tag node instance
        :param tag_class:
        :param template:
        :return:
        """
        template = "{{% load {} %}} {}".format(tag_lib, template)
        template = self.compile_template(template, tag_lib=tag_lib)
        return template.nodelist.get_nodes_by_type(tag_class)[0]

    def compile_template(self, template, tag_lib="compile_tags"):
        """
        compile_tag compiles template and returns tag node instance
        :param tag_lib: tag_library name that will be loaded in template
        :param template:
        :return:
        """
        template = "{{% load {} %}} {}".format(tag_lib, template)
        return self.engine.from_string(template)

    def test_options(self):
        class TestTag(Tag):
            class Meta:
                pass

        self.assertEqual(TestTag._meta.start_tag, "test")
        self.assertEqual(TestTag._meta.end_tag, "end:test")
        self.assertEqual(TestTag._meta.namespace, None)

    def test_arguments_order(self):
        """
        test arguments with mixins and inherited tags
        :return:
        """

        class BaseTag(Tag):
            first = Keyword()
            second = Keyword()
            third = Keyword()

        class TestTagMixin:
            fourth = Positional()
            fifth = Positional()
            sixth = Positional()

        class TestTag(TestTagMixin, BaseTag):
            seventh = KeywordGroup("some_<ident>")
            eighth = KeywordGroup(("some_<ident>", "other_<ident>"))

        expected = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth']
        self.assertSequenceEqual(list(TestTag.arguments.keys()), expected)

    def test_arguments_positional(self):
        # from .templatetags.compile_tags import TestCompileTag
        template = self.compile_template(
            """
            {% test_compile 4 5 6 7 first="million" second="billion" %}
                is this the real life
                {% test_compile 8 9 10 first="aleven" second="twelve" %}
                    is this just fantasy
                {% end:test_compile %}
            {% end:test_compile %}
            {% test_compile 1 2 3 first="value" second="other" %}
                Caught in a landslide,
                No escape from reality.
            {% end:test_compile %}
            """
        )
        rendered = template.render(Context({}))
        self.assertIn("is this the real life", rendered)
        self.assertIn("is this just fantasy", rendered)
        self.assertIn("Caught in a landslide,", rendered)
        self.assertIn("No escape from reality.", rendered)

    def test_invalid_tag_not_inherit_from_tag(self):
        with self.assertRaises(ImproperlyConfigured):
            @register_tag(None)
            class _:
                pass

    def test_arguments_keyword_choices(self):

        def inst_tag(template):
            from tests.templatetags.arguments_tags import TestArgumentsCleanTag
            return self.compile_tag(TestArgumentsCleanTag, template, tag_lib="arguments_tags")

        data = [
            # val     # expect
            ["wrong", "one"],
            ["two", "two"],
            ["three", "three"],
        ]

        for item in data:
            value, expected = item
            tag = inst_tag('{% test_arguments_clean first="' + value + '" %}{% end:test_arguments_clean %}')
            self.assertEqual(tag.get_render_data(Context(), {})['arguments']['first'], expected)

        # test default value
        tag = inst_tag('{% test_arguments_clean %}{% end:test_arguments_clean %}')
        self.assertEqual(tag.get_render_data(Context(), {})['arguments']['first'], 'one')

    def test_arguments_positional_choices(self):

        def inst_tag(template):
            from tests.templatetags.arguments_tags import TestArgumentsPositionalCleanTag
            return self.compile_tag(TestArgumentsPositionalCleanTag, template, tag_lib="arguments_tags")

        data = [
            # val     # expect
            ["1", 1],
            ["2", 2],
            ["8", 3],
        ]

        for item in data:
            value, expected = item
            tag = inst_tag(
                '{% test_arguments_positional_clean ' + value + ' %}{% end:test_arguments_positional_clean %}')
            self.assertEqual(tag.get_render_data(Context(), {})['arguments']['positional'], expected)

    def test_arguments_positional_validation(self):
        def inst_tag(template, context):
            tag = self.compile_tag(arguments_tags.TestArgumentsPositionalValidation, template, tag_lib="arguments_tags")
            data = tag.get_render_data(Context, {})
            return tag, data

        tag, data = inst_tag(
            "{% test_arguments_positional_validators 5 %}{% end:test_arguments_positional_validators %}",
            Context()
        )

        self.assertEqual(data["arguments"]["positional"], 2)

        tag, data = inst_tag(
            "{% test_arguments_positional_validators 4 %}{% end:test_arguments_positional_validators %}",
            Context()
        )

        self.assertEqual(data["arguments"]["positional"], 4)
