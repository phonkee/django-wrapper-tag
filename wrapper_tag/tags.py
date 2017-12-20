"""
@author 'Peter Vrba <phonkee@phonkee.eu>'
"""
import collections
import copy

from django.template.base import Context, Node, TemplateSyntaxError

from . import utils
from .arguments import Argument
from .options import Options
from .rendered import RenderedTag


class TagMeta(type):
    """
    Metaclass that collects Arguments declared on the base classes. It also prepares tag options.
    """

    def __new__(mcs, name, bases, attrs):
        """
        __new__ creates new tag class

        It reads `Meta` options first

        :param name: new class name
        :param bases: bases that class inherits from
        :param attrs: attributes of class (should be ordered dict in python 3)
        :return:
        """
        # get Meta class options
        meta = attrs.get('Meta', None)

        # if Meta not found on class, try to find on base classes
        if not meta:
            for base in reversed(bases):
                meta = getattr(base, 'Meta', None)
                if meta:
                    break

        # parse Meta class (options)
        options = Options(meta, cls_name=name)

        # create new class
        new_class = super().__new__(mcs, name, bases, attrs)
        new_class._meta = options

        # prepare current arguments
        cur_args = collections.OrderedDict()

        # find arguments on class
        for key, value in list(attrs.items()):
            if isinstance(value, Argument):

                # name is already set
                if value.name is None:
                    value.name = key

                cur_args[key] = value

                # remove from class
                attrs.pop(key)

        attrs['_decl_args'] = cur_args

        # prepare declared arguments
        declared_arguments = collections.OrderedDict()

        for base in reversed(new_class.__mro__):
            if hasattr(base, '_decl_args'):
                # inherited tag
                declared_arguments.update(getattr(base, '_decl_args'))
            else:
                # tag mixin support
                for key, value in list(base.__dict__.items()):
                    if isinstance(value, Argument):
                        value.name = key
                        declared_arguments[key] = value
        # store declared_arguments
        attrs['_decl_args'] = declared_arguments

        return new_class

    def __init__(cls, name, bases, attrs):
        """
        __init__ is called at class creation time

        @TODO: move this code into __new__

        :param name: class name
        :param bases: base classes
        :param attrs: attributes dict
        """

        # Add arguments to tag class
        cls.arguments = copy.deepcopy(attrs['_decl_args'])

        # call contribute_to_class to add possibility for arguments to alter tags
        for arg_name, arg in cls.arguments.items():
            arg.contribute_to_class(cls, name)

        # call parent
        super().__init__(name, bases, attrs)

    def __call__(cls, nodelist, parsed_args, parsed_kwargs, varname):
        """
        __call__ is called when new instance is created.

        what we do here?

        * first we need to deepcopy arguments so we have unique instances
        * assign parsed args/kwargs

        :param nodelist:
        :param parsed_args:
        :param parsed_kwargs:
        :param varname:
        :return:
        """
        self = super().__call__()
        self.arguments = copy.deepcopy(cls.arguments)

        self.nodelist = nodelist
        self.varname = varname

        # now we should set default values
        for arg_name, arg in self.arguments.items():
            # claim arguments on every argument and store to instance under arg name
            value = arg.claim_arguments(parsed_args, parsed_kwargs)

            setattr(self, arg_name, value)

        if self.varname is None and self._meta.as_var_only and utils.is_template_debug():
            raise TemplateSyntaxError(
                "tag {} can be only rendered to variable, not printed directly.".format(self._meta.start_tag))

        # now we should have all parsed_args and parsed_kwargs claimed
        # all remaining args/kwargs are unhandled
        # when template debug is enabled we raise exception, otherwise we just ignore args/kwargs

        if parsed_args and utils.is_template_debug():
            raise TemplateSyntaxError(
                'Tag `{}` received unhandled args: {}'.format(self._meta.start_tag, parsed_args))

        if parsed_kwargs and utils.is_template_debug():
            raise TemplateSyntaxError('Tag `{}` received unhandled kwargs: {}'.format(
                self._meta.start_tag, parsed_kwargs.keys()))

        return self


class BaseTag(metaclass=TagMeta):
    """
    BaseTag uses TagMeta metaclass
    """
    varname = None
    nodelist = None
    arguments = None

    args_values = None

    @classmethod
    def compile(cls, parser, token):
        """
        compile method parses arguments (positional, keyword) and verifies that all belong to arguments.
        If not template error is raised.
        :param parser:
        :param token:
        :return:
        """
        nodelist = parser.parse((cls._meta.end_tag,))
        varname = None
        bits = token.split_contents()[1:]

        # parse "as_var" variable
        if len(bits) >= 2 and bits[-2] == 'as':
            varname = bits[-1]
            bits = bits[:-2]

        # parse args and kwargs from tag
        parsed_args, parsed_kwargs = utils.parse_bits(parser, bits, cls._meta.start_tag)

        # die token die
        parser.delete_first_token()

        return cls(nodelist, parsed_args, parsed_kwargs, varname)

    def generate_id(self):
        """
        generate_id generates random id for rendered elements (every render is different)
        :return:
        """
        return next(utils.unique_id)


WRAPPER_TAG_KEY = 'wrapper_tag'
PARENT_WRAPPER_TAG_KEY = 'parent'
CONTENT_TAG = 'content'


class Tag(BaseTag, Node):
    """
    Tag class

    Every wrapper tag should inherit from this tag.
    """

    def get_render_data(self, context: Context, parent_tag: dict) -> dict:
        """
        get_render_data gets all values from all arguments, and also calls render_<field> method
        :param context: template context
        :param parent_tag: parent_tag information
        :return:
        """
        render_data = {
            "id": self.generate_id(),
            "name": self._meta.start_tag,
            "arguments": {},
        }

        # add parent_tag if available
        if parent_tag:
            render_data[PARENT_WRAPPER_TAG_KEY] = parent_tag

        # now iterate over all arguments and get values resolved
        for arg_name, arg in self.arguments.items():

            # we got value which is either FilterExpression, list<FilterExpression>, dict
            arg_value = getattr(self, arg_name, None)
            arg_value = arg.get_value(context, arg_value)

            # run full clean
            arg_value = arg.full_clean(self, arg_value)

            # only non None values are added
            if arg_value is not None:
                render_data["arguments"][arg_name] = arg_value

        # now when we have all argument values collected, we need to call all render_<argument> methods
        # prepare dict for rendering arguments values
        rendered_args = {}

        # iterate over all arguments and call `render_<field>` methods.
        for tag_name, tag in self.arguments.items():
            try:
                rendered = tag.render(context, render_data, self)
                if rendered is None:
                    continue
                rendered_args["{}__rendered".format(tag_name)] = rendered
            except NotImplementedError:
                continue

        # update with rendered data
        render_data["arguments"].update(rendered_args)

        return render_data

    def render(self, context: Context):
        """
        :param context:
        :return:
        """

        # try to get parent tag
        parent_tag = context.get(WRAPPER_TAG_KEY, None)

        # first get all arguments data by given context
        render_data = self.get_render_data(context, parent_tag)

        # now we need to render inside nodelist. we should add "parent_tag" to context so children have access
        # to our data.
        with context.push() as context_dict:
            # for nodelist data we should provide tag values
            context_dict[WRAPPER_TAG_KEY] = render_data

            # render nodes
            nodes_rendered = self.nodelist.render(context)

        # now we need to render wrapper with all the data we have
        # children wrapper_tags can communicate to parent data so we have bi-directional comunication
        # this is particularly useful in scenarios where we have "items" such as in accordion etc..
        # these items should push data on parent wrapper tag data
        # for this we have render_tag method that should be called
        rendered_tag = self.render_tag(context, nodes_rendered, render_data)
        if isinstance(rendered_tag, RenderedTag):
            pass
        else:
            rendered_tag = RenderedTag(rendered_tag, render_data)

        # stored to context under self.varname
        # we don't pop the context since we need to store the value
        if self.varname:
            # store value to context and push one context
            context_dict = context.push()
            context_dict[self.varname] = rendered_tag

        return rendered_tag

    def render_tag(self, context: Context, content: str, render_data: dict):
        """
        Override this method if you need custom rendering of tag
        :param context: template context
        :param content:
        :param render_data:
        :return:
        """

        with context.push() as context_dict:
            context_dict[WRAPPER_TAG_KEY] = render_data
            context_dict[CONTENT_TAG] = content
            template = self._meta.get_template()
            rendered = template.render(context.flatten())

        return RenderedTag(rendered, self._meta.start_tag, **render_data)
