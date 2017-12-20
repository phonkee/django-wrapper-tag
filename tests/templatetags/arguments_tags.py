from django.core.exceptions import ValidationError
from django.template.library import Library

from wrapper_tag import register_tag, Tag, Keyword, Positional

register = Library()


@register_tag(register)
class TestArgumentsCleanTag(Tag):
    first = Keyword(choices=("one", "two", "three"), default="one")

    class Meta:
        start_tag = "test_arguments_clean"
        template = "{{ content }}"


@register_tag(register)
class TestArgumentsPositionalCleanTag(Tag):
    positional = Positional(choices=(1, 2, 3, 4, 5), default=3)

    class Meta:
        start_tag = "test_arguments_positional_clean"
        template = "{{ content }}"


def is_even_validator(value):
    if value % 2 == 1:
        raise ValidationError("nope")


@register_tag(register)
class TestArgumentsPositionalValidation(Tag):
    positional = Positional(default=2, validators=(is_even_validator,))

    class Meta:
        start_tag = "test_arguments_positional_validators"
        template = "{{ content }}"
