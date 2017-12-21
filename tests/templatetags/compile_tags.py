"""
@author 'Peter Vrba <phonkee@phonkee.eu>'
"""

from django.template.library import Library

from wrapper_tag import register_tag, Tag, KeywordGroup, Keyword, Positional

register = Library()


@register_tag(register)
class TestCompileTag(Tag):
    # patterns for regular expressions
    PATTERNS = (
        "group_<str>",
    )

    positional = Positional()

    first = Keyword()
    second = Keyword()
    third = Keyword()

    groupper = KeywordGroup(PATTERNS)
    star = Positional(is_varargs=True)

    class Meta:
        start_tag = "test_compile"
        template = "{{ content }}"

    def render_first(self, data, **kwargs):
        return "ohohoooo"
