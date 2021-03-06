from __future__ import absolute_import, print_function, unicode_literals

from collections import defaultdict

import six
from django import template
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wrapper_tag import arguments, validators, utils

IDENTITY_ID_RAND_MAX = 2 ** 32


def tag_attributes_default(cls):
    """
    :param cls:
    :return:
    """
    return defaultdict(utils.StringSet)


class TagAttributes(object):
    attrs = arguments.KeywordGroup(readonly=True, default=tag_attributes_default)

    def render_attrs(self, argument, data, context):
        attrs = data.get(argument.name, self.arguments[argument.name].default)
        full = ' '.join(['{}="{}"'.format(key, value) for key, value in six.iteritems(attrs) if value])
        full = ' ' + full if full else ''
        return mark_safe(full)


def id_data_callback(data, **kwargs):
    """
    Add id to attrs
    """
    if 'attrs' in data:
        data['attrs']['id'].add(data['id'])


class Identity(TagAttributes):
    id = arguments.Keyword(on_data=id_data_callback, help_text=_('html id attribute'))
    name = arguments.Keyword(help_text=_('html name attribute'))

    def clean_id(self, argument, value):
        """
        Try to clean id, if not given generate one
        """
        if not value:
            return utils.generate_id()
        return value

    def render_id(self, argument, data, context):
        """
        Custom render for argument `id`
        """
        if 'id' in data and data['id']:
            return format_html('id="{id}"', **data)

    def render_name(self, argument, data, context):
        """
        Custom rende method for argument `name`
        """
        if 'name' in data and data['name']:
            return format_html('name="{name}"', **data)


def css_class_data_callback(data, **kwargs):
    """
    Check if TagAttributes
    """

    if 'attrs' in data and 'attrs' in data:
        data['attrs']['class'].add(data['css_class'])


class CssClass(object):
    """
    Adds ability to set cusom css_class
    """
    css_class = arguments.Keyword(default='', help_text='Additional css class (e.g. ``"class1 class2"``)',
                                  on_data=css_class_data_callback)


"""
Old mixins




"""


class Data(object):
    """
    Data handles kwarguments for `data-` html attributes.
    """
    data = arguments.KeywordGroup('data_*', help_text='data attributes, data_* will be converted to data-*')

    def render_data(self, argument, data, context=None):
        """
        Render data-* html attributes
        :param attr: attribute instance
        :param data: whole tag data
        :param context: context for rendering
        :return:
        """
        value = data.get(argument.name, {})
        return ' '.join(['{}="{}"'.format(k.replace('_', '-'), v) for k, v in six.iteritems(value)])


class Tag(object):
    """
    Add ability to set custom tag.
    """

    # override these properties to customize tag mixin
    TAG_CHOICES = ['div']
    TAG_DEFAULT = 'div'

    tag = arguments.Keyword(help_text='tag of html element', choices=lambda x: Tag.TAG_CHOICES,
                            default=lambda x: Tag.TAG_DEFAULT,
                            tag_render_method="render_html_tag")


class Hyperlink(object):
    """
    Adds ability to provide href functionality
    """
    href = arguments.Hyperlink(help_text=_('raw href (url takes precedence)'))


class Size(object):
    size = arguments.KeywordGroup(('xs', 'sm', 'md', 'lg'))

    def render_size(self, argument, data, context):
        lines = []
        for key, value in six.iteritems(argument.filter_data(data.get(argument.name, {}))):
            lines.append(self.format_size(key, value))
        return " ".join(lines)

    def format_size(self, key, value):
        return format_html('col-{key}-{value}'.format(key=key, value=value))


def tooltip_contribute_data(data, **kwargs):
    """
    @TODO: fix this
    :param tag:
    :param data:
    :return:
    """
    return

    value = data['tag']

    if value is None:
        return

    from wrapper_tag import RenderedTag

    if 'data' not in data:
        data['data'] = {}

    if isinstance(value, RenderedTag):
        data['data']['rel'] = 'tooltip'
        data['data']['data_placement'] = value.attributes['position']
        data['data']['original_title'] = value.attributes['content']
        data['data']['title'] = value.attributes['content']
    else:
        data['data']['rel'] = 'tooltip'
        data['data']['original_title'] = value
        data['data']['title'] = value

    return data


class Tooltip(Data):
    tooltip = arguments.Keyword(help_text='Tooltip support (either rendered tooltip or string',
                                validators=validators.AnyValidator(
                                    validators.RequiresTagValidator('tooltip'),
                                    validators.StringValidator()
                                ),
                                on_data=tooltip_contribute_data
                                )


class Common(Identity, CssClass, Data, Tag):
    """
    common mixin used in most of wrapper tags.
    """


class ColorMixin(object):
    AVAILABLE_COLORS = (
        'green', 'greenDark', 'greenLight',
        'purple', 'magenta',
        'pink', 'pinkDark',
        'blue', 'blueLight', 'blueDark',
        'teal',
        'yellow',
        'orange',
        'orangeDark',
        'red',
        'redLight',
    )

    def get_bg_color_css_class(self, value):
        if not value:
            return
        return 'bg-color-{}'.format(value)

    def get_text_color_css_class(self, value):
        if not value:
            return
        return 'txt-color-{}'.format(value)

    def get_color_class(self, value, prefix='txt'):
        if not value:
            return
        return '{}-color-{}'.format(prefix, value)


class BackgroundColorMixin(ColorMixin):
    bg_color = arguments.Keyword(choices=ColorMixin.AVAILABLE_COLORS)

    def render_bg_color(self, argument, data, context):
        return self.get_color_class(data.get(argument.name, None), 'bg')


class TextColorMixin(ColorMixin):
    AVAILABLE_COLORS = ColorMixin.AVAILABLE_COLORS + (
        'muted',
        'primary',
        'success',
        'danger',
        'warning',
        'info',
    )

    text_color = arguments.Keyword(choices=AVAILABLE_COLORS)

    def render_text_color(self, argument, data, context):
        return self.get_color_class(data.get(argument.name, None), 'txt')


class ExtraContent(object):
    """
    ExtraContent mixin provides extra_content to template.
    """

    @property
    def extra_content_template(self):
        raise TemplateSyntaxError('ExtraContent mixin needs extra_content_template property.')

    def render_tag(self, tag_kwargs, context):
        context['extra_content'] = render_to_string(self.extra_content_template, context)
        print(context['extra_content'])
        rendered = super(ExtraContent, self).render_tag(tag_kwargs, context)
        print("rendered", rendered)

        return rendered