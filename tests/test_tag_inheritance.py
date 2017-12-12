"""
test_django-wrapper-tag
------------
Tests for `django-wrapper-tag` inheritance of tags module.
"""

from django.test import TestCase

from wrapper_tag import arguments
from wrapper_tag import tag


class TestInheritanceTag(TestCase):

    def test_something(self):
        class FirstTag(object):
            title11 = arguments.Keyword()
            title12 = arguments.Keyword()

        class SecondTag(FirstTag):
            title21 = arguments.Keyword()
            title22 = arguments.Keyword()

        class ThirdTag(SecondTag, tag.Tag):
            title31 = arguments.Keyword()
            title32 = arguments.Keyword()

        class FourthTag(ThirdTag):
            title41 = arguments.Keyword()
            title42 = arguments.Keyword()

            @classmethod
            def contribute_to_class(cls, name):
                pass

        self.assertEqual(len(FourthTag.arguments), 8, 'inheritance is probably not working')
