from __future__ import absolute_import, print_function, unicode_literals

import random
import re

import six
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wrapper_tag import arguments, validators, utils


IDENTITY_ID_RAND_MAX = 2 ** 32


class TagAttributes(object):

    attrs = arguments.KeywordGroup(readonly=True)

    def render_attrs(self, argument, data, context):
        attrs = data.get(argument.name, {})
        full = ' '.join(['{}="{}"'.format(key, value) for key, value in six.iteritems(attrs)])
        full = ' ' + full if full else ''
        return mark_safe(full)


def id_data_callback(tag, data):
    """
    Add id to attrs
    """
    if 'attrs' in data:
        data['attrs']['id'] = data['id']
    return data


class Identity(TagAttributes):

    id = arguments.Keyword(data_callback=id_data_callback)
    name = arguments.Keyword()

    def clean_id(self, argument, value):
        """
        Try to clean id, if not given generate one
        """
        if not value:
            return 'id_{}'.format(random.randint(0, IDENTITY_ID_RAND_MAX))
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


def css_class_data_callback(tag, data):
    """
    Check if TagAttributes
    """
    if 'attrs' in data and 'css_class' in data:
        data['attrs']['class'] = data['css_class']
    return data


class CssClass(object):
    """
    Adds ability to set cusom css_class
    """
    css_class = arguments.Keyword(default='', help_text='Additional css class (e.g. ``"class1 class2"``)',
                                  data_callback=css_class_data_callback)


"""
Old mixins




"""


class JsEvents(object):

    js_events = arguments.KeywordGroup(readonly=True)

    def render_js_events(self, argument, data, context):
        """
        Renders javascript event handlers.
        :param argument:
        :param data:
        :param context:
        :return:
        """
        if 'id' not in data or not data['id']:
            return ''

        js_events = data.get('js_events', {})
        OBJ_NAME = '$obj'

        lines = []

        for js_event in js_events.keys():
            if js_event not in argument.extra_data:
                continue

            lines.append(
                argument.extra_data[js_event].format(object=OBJ_NAME, function=js_events[js_event])
            )

        if not lines:
            return ''

        lines.insert(0, 'var {obj_name} = $("#{id}");'.format(obj_name=OBJ_NAME, **data))
        result = format_html('<script type="text/javascript">$(function() {{ {script} }});</script>',
                             script=mark_safe("".join(lines)))
        return result


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

    tag = arguments.Keyword(help_text='tag', choices=lambda x: Tag.TAG_CHOICES, default=lambda x: Tag.TAG_DEFAULT,
                            tag_render_method="render_html_tag")


class Hyperlink(object):
    """
    Adds ability to provide href functionality
    """
    href = arguments.Keyword(help_text=_('raw href (url takes precedence)'))
    url = arguments.KeywordGroup(('url', 'url_kwarg_*', 'url_arg_*'),
                                 help_text=_('if provided, href will be set with call to url reverse'))
    url_query = arguments.Keyword(help_text=_('if provided, will be added as url query params.'))

    def render_href(self, argument, data, context=None):
        """
        custom href rendering
        :param attribute:
        :param data:
        :return:
        """
        if 'url' in data and 'reversed' in data['url']:
            return format_html('href="{reversed}"'.format(**data['url']))

        if 'href' in data and data['href']:
            return format_html('href="{href}"'.format(**data))

    def clean_url(self, argument, data):
        """
        clean_url tries to resolve given url

        @TODO: fix this
        :param argument:
        :param data:
        :return:
        """

        if 'url' not in data:
            return data

        kwarg_keys = utils.find_elements('url_kwarg_*', data.keys())
        arg_keys = utils.find_elements('url_arg_*', sorted(data.keys()))
        url_kwargs = {k.lstrip('url_kwarg_'): v for k, v in six.iteritems(data) if k in kwarg_keys}
        url_args = [data[v] for v in arg_keys]

        data['reversed'] = reverse(data['url'], args=url_args, kwargs=url_kwargs)
        if 'url_query' in data and data['url_query']:
            data['reversed'] = '{}?{}'.format(data['reversed'], data['url_query'])
        return data


class Icon(object):

    icon = arguments.Keyword(default='', help_text=_('fontawesome icon name (e.g. `user`)'))

    def render_icon(self, argument, data, context=None):
        # hack for now
        # data['iconset'] = 'fa'
        # print '<i class="{iconset} {iconset}-{name}"></i>'.format(**data)
        # @TODO: check this code
        # self.logger.debug("this is icon data %s", data)

        if 'icon' in data and data['icon']:
            return format_html('<i class="fa fa-{}"></i>', data['icon'])


class Size(object):

    size = arguments.KeywordGroup(('xs', 'sm', 'md', 'lg'))

    def render_size(self, argument, data, context):
        lines = []
        for key, value in six.iteritems(argument.filter_data(data.get(argument.name, {}))):
            lines.append(self.format_size(key, value))
        return " ".join(lines)

    def format_size(self, key, value):
        return format_html('col-{key}-{value}'.format(key=key, value=value))


def tooltip_contribute_data(tag, data):
    """
    @TODO: fix this
    :param tag:
    :param data:
    :return:
    """
    return data

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
                                data_callback=tooltip_contribute_data
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


class ModalJsEvents(JsEvents):
    js_events = arguments.KeywordGroup(('on_show', 'on_after_show', 'on_hide', 'on_after_hide', 'on_data_load'),
                                       extra_data={
                                           'on_show': '{object}.on("show.bs.modal", {function});',
                                           'on_after_show': '{object}.on("shown.bs.modal", {function});',
                                           'on_hide': '{object}.on("hide.bs.modal", {function});',
                                           'on_after_hide': '{object}.on("hidden.bs.modal", {function});',
                                           'on_data_load': '{object}.on("loaded.bs.modal", {function});',
                                       })
