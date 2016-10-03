from __future__ import absolute_import, print_function, unicode_literals

import copy
from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.dispatch import Signal
from django.template.exceptions import TemplateSyntaxError
from django.template import Node
from django.utils import six

from wrapper_tag import utils
from wrapper_tag import arguments
from wrapper_tag import rendered

from logging import getLogger, DEBUG


logger = getLogger('wrapper_tag.tags')


class TagOptions(utils.TemplateMixin):
    """
    Tag options stored as `Meta` class on tag
    """

    _start_tag = None
    end_tag = None

    def __init__(self, options=None, tag_name=None):
        self.start_tag = getattr(options, 'start_tag', None)

        # if no start_tag is given, we construct it from tag class name
        if not self.start_tag:
            if tag_name.lower().endswith('tag'):
                tag_name = tag_name[:-3]
            self.start_tag = utils.camel_to_separated(tag_name)

        end_tag = getattr(options, 'end_tag', None)
        if end_tag:
            self.end_tag = end_tag

        self.as_var_only = bool(getattr(options, 'as_var_only', False))
        self.aliases = getattr(options, 'aliases', [])
        self.tag_name = tag_name

        super(TagOptions, self).__init__(template=getattr(options, 'template', None),
                                         template_name=getattr(options, 'template_name', None))

    @property
    def start_tag(self):
        return self._start_tag

    @start_tag.setter
    def start_tag(self, start_tag):
        self._start_tag = start_tag
        self.end_tag = 'end:{}'.format(start_tag)

    @property
    def template_errors(self):
        return {
            'no_template': 'Tag `{}` doesn\'t provide template or template_name'.format(self.start_tag),
        }

    def __repr__(self):
        return '<Options for %s>' % self.tag_name


# noinspection PyUnresolvedReferences
class TagMetaclass(type):
    """
    Metaclass that collects Arguments declared on the base classes. It also prepares tag options.
    """

    def __new__(mcs, name, bases, attrs):
        options = TagOptions(attrs.get('Meta', None), tag_name=name)
        current_arguments = []

        # add logger if not provided
        if 'logger' not in attrs:
            attrs['logger'] = utils.get_sub_logger(logger, options.start_tag)

        for key, value in list(attrs.items()):
            if isinstance(value, arguments.Argument):
                # set argument name
                value.name = key
                current_arguments.append((key, value))
                attrs.pop(key)

        current_arguments.sort(key=lambda x: x[1].creation_counter)

        attrs['_declared_arguments'] = OrderedDict(current_arguments)
        attrs['rtc_ids'] = {}

        # # set _decorated_function for template Library.tag so it gets correct name for tag.
        # def fake_func():
        #     pass  # pragma: no cover
        # fake_func.__name__ = options.start_tag
        # attrs['_decorated_function'] = fake_func
        attrs['name'] = options.start_tag

        # create new class
        new_class = super(TagMetaclass, mcs).__new__(mcs, name, bases, attrs)
        new_class.options = options

        # prepare declared arguments
        declared_arguments = OrderedDict()
        for base in reversed(new_class.__mro__):
            if hasattr(base, '_declared_arguments'):  # inherited tag
                declared_arguments.update(base._declared_arguments)
            else:  # tag mixin support
                base_arguments = []
                for key, value in list(base.__dict__.items()):
                    if isinstance(value, arguments.Argument):
                        value.name = key
                        base_arguments.append((key, value))

                # sort arguments
                base_arguments.sort(key=lambda x: x[1].creation_counter)
                declared_arguments.update(OrderedDict(base_arguments))

        # store declared_arguments
        new_class._declared_arguments = declared_arguments

        return new_class

    def __init__(cls, name, bases, attrs):
        """
        __init__ is called at class creation time
        :param name: class name
        :param bases: base classes
        :param attrs: attributes dict
        """
        # Add arguments to tag class
        cls.arguments = copy.deepcopy(cls._declared_arguments)

        # signals
        cls.on_data = Signal(providing_args=["data", "context"])
        cls.on_rendered_tag = Signal(providing_args=["rendered_tag", "data", "context"])

        super(TagMetaclass, cls).__init__(name, bases, attrs)

        # contribute argument to tag class
        for name, argument in six.iteritems(cls.arguments):
            argument.logger = utils.get_sub_logger(cls.logger, argument.name)
            argument.contribute_to_class(cls, name)


# noinspection PyUnresolvedReferences
class BaseTag(object):
    """
    BaseTag provides compile function (constructor) and also render method
    """
    args = None
    kwargs = None
    varname = None
    nodelist = None
    data_callbacks = []
    arguments = []

    # signals
    on_data = None
    on_rendered_tag = None

    def __init__(self, parser, token):
        """
        Compile function
        :param parser:
        :param token:
        """

        # empty data_callbacks
        self.data_callbacks = []

        # parse here all args, kwargs...
        self.nodelist = parser.parse((self.options.end_tag,))

        bits = token.split_contents()[1:]

        # parse "as" variable
        if len(bits) >= 2 and bits[-2] == 'as':
            self.varname = bits[-1]
            bits = bits[:-2]

        # parse args and kwargs
        self.args, self.kwargs = utils.parse_bits(parser, bits, self.options.start_tag)

        # die token die
        parser.delete_first_token()

    @classmethod
    def add_data_callback(cls, data_callback):
        """
        Adds single data_callback function to tag class
        :param data_callback:
        :return:
        """
        cls.data_callbacks.append(data_callback)

    def get_tag_data(self, context):
        """
        Return tag kwargs for render
        :param context:
        :return:
        """
        kwargs = dict([(key, value.resolve(context)) for key, value in self.kwargs.items()])
        args = list([value.resolve(context) for value in self.args])
        tag_data = {}

        # iterate over arguments and call get_tag_value on it
        for _, argument in six.iteritems(self.arguments):
            value = argument.get_tag_value(args, kwargs)

            # clean the value
            value = argument.full_clean(self, value)

            if value is not None:
                tag_data[argument.name] = value

        # unhandled args
        if utils.get_config().template_debug and args:
            raise TemplateSyntaxError('Tag `{}` received unhandled args: {}'.format(self.options.start_tag, args))

        # unhandled kwargs
        if utils.get_config().template_debug and kwargs:
            raise TemplateSyntaxError('Tag `{}` received unhandled kwargs: {}'.format(
                self.options.start_tag, kwargs.keys()))

        # dispatch on_data signal
        self.__dispatch_on_data(tag_data, context)

        # render all arguments
        for _, argument in six.iteritems(self.arguments):
            argument.logger.debug('Rendering with: %s', tag_data)

            tmp = argument.full_render(self, tag_data, context=context)
            if tmp is utils.NULL or tmp is None:
                continue
            tag_data['{}__rendered'.format(argument.name)] = tmp

        return tag_data

    def render(self, context):
        """
        Render method does multiple steps

        * resolve args/kwargs
        * iterate over all arguments and call get_tag_value
        """
        tag_kwargs = self.get_tag_data(context)
        self.logger.debug("Rendering with: %s", tag_kwargs)

        # render content which is isolated from tag data
        tag_kwargs['content'] = self.nodelist.render(context)

        # render tag to variable
        rendered_tag = self.render_tag(tag_kwargs, context)

        # check if render_tag returned RenderedTag, if not wrap the text into it
        if not isinstance(rendered_tag, rendered.RenderedTag):
            rendered_tag = rendered.RenderedTag(rendered_tag, self.options.start_tag)

        # dispatch on_rendered_tag
        self.__dispatch_on_rendered_tag(rendered_tag, tag_kwargs, context)

        # stored to context under self.varname
        if self.varname:
            try:
                context[self.varname]
            except KeyError:
                pass
            else:
                if utils.is_template_debug():
                    raise TemplateSyntaxError('variable {} already exists on context'.format(self.varname))

            # store value to context and push one context
            context[self.varname] = rendered_tag
            context.push({})

            return ''

        # check if tag is intended as_var_only (can be only stored to variable, not print directly
        if self.options.as_var_only and not self.varname and is_template_debug():
            raise ImproperlyConfigured('Tag `{}` must be assigned to variable using `as variable`.'.format(
                self.options.start_tag))

        return rendered_tag

    def render_tag(self, tag_kwargs, context):
        """
        The method you should override in your custom tags
        """
        tmp = ''
        with context.push(**tag_kwargs):
            template = self.options.template
            if template is None:
                raise ImproperlyConfigured("tag: {}, error: please provide meta.template_name or meta.template".format(
                                           self.options.start_tag))
            tmp = template.render(context)
        return rendered.RenderedTag(tmp, self.options.start_tag)

    def __dispatch_on_data(self, data, context):
        """
        Dispatch on_data signal
        :param data: tag data
        :param context: context
        :return:
        """
        result = self.on_data.send_robust(sender=self.__class__, data=data, context=context)

        if self.logger.isEnabledFor(DEBUG):
            for method, error in result:
                if error:
                    self.logger.error('on_rendered_tag: %s, returned error: %s', method, error)

    def __dispatch_on_rendered_tag(self, rendered_tag, data, context):
        """
        Dispatch on_rendered_tag signal
        :param rendered_tag:
        :param data:
        :param context:
        :return:
        """
        result = self.on_rendered_tag.send_robust(sender=self.__class__, rendered_tag=rendered_tag, data=data,
                                                  context=context)

        if self.logger.isEnabledFor(DEBUG):
            for method, error in result:
                if error:
                    self.logger.error('on_rendered_tag: %s, returned error: %s', method, error)


class Tag(six.with_metaclass(TagMetaclass, BaseTag, Node)):
    """
    Main tag to inherit from
    """
