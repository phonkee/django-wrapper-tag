import copy

from django.core.exceptions import ValidationError
from django.template import Context, TemplateSyntaxError

from wrapper_tag import globstr
from wrapper_tag import utils


class Argument:
    # argument name in tag definition
    name = None

    # choices
    choices = None

    # default value
    default = None

    # help text for argument (used in documentation)
    help_text = None

    # store name of method
    _render_method_name = None

    # list of validators
    _validators = None

    def __init__(self, name=None, default=None, choices=None, help_text=None, render_method=None, validators=None):
        """
        construct base argument
        :param default:
        :param name:
        :param help_text:
        """
        self.choices = choices or []
        self.default = default
        self.name = name
        self.help_text = help_text
        self._render_method_name = render_method
        self._validators = validators or []
        if not utils.is_seq(self._validators):
            self._validators = list(self._validators)

    def claim_arguments(self, args: list, kwargs: dict):
        """
        argument should get args/kwargs that he needs
        :param args:
        :param kwargs:
        """

    @property
    def clean_method_name(self) -> str:
        """
        clean_method_name returns method name on tag instane
        :return:
        """
        return "clean_{}".format(self.name)

    def contribute_to_class(self, cls, name):
        """
        Arguments can contribute when tag class is created.
        :param cls:
        :param name:
        :return:
        """

        render_method = getattr(cls, self.render_method_name, None)

        if render_method is None:
            def blank(self, context, data, **kwargs):
                raise NotImplementedError

            # set method to blank one
            setattr(cls, self.render_method_name, blank)
        else:
            if utils.is_template_debug():
                utils.verify_func_signature(render_method, "context", "data", "**kwargs")

        clean_method = getattr(cls, self.clean_method_name, None)
        if clean_method is None:
            def clean_default(self, value, **kwargs):
                raise NotImplementedError

            setattr(cls, self.clean_method_name, clean_default)
        else:
            if utils.is_template_debug():
                utils.verify_func_signature(clean_method, "value", "**kwargs")

    def full_clean(self, tag_instance, value):
        """
        full_clean performs full clean on value, following steps are run

        * check if value in choices
        * run all validators
        * call clean_<attribute> method on tag

        :param tag_instance:
        :param value:
        :return:
        """

        # first check against choices
        if self.choices:
            if value not in self.choices:
                value = self.get_default()

        # run validators
        if self._validators:
            for validator in self._validators:
                try:
                    validator(value)
                except ValidationError:
                    value = self.get_default()
                    break
                except Exception:
                    # unknown exception
                    value = self.get_default()
                    break

        # now run custom clean method
        try:
            value = getattr(tag_instance, self.clean_method_name)(value)
        except ValidationError:
            value = self.get_default()
        except NotImplementedError:
            pass
        except Exception:
            pass

        return value

    def get_default(self):
        """
        get_default returns default value
        :return:
        """
        if callable(self.default):
            return self.default()

        return copy.deepcopy(self.default)

    def get_value(self, _: Context, value):
        """
        returns value from given context
        :param _: context
        :param value: value that contains or is FiterExpression
        """
        return self.default

    def render(self, context: Context, data: dict, tag):
        """
        render renders attribute
        :param context:
        :param data:
        :param tag:
        :return:
        """
        result = getattr(tag, self.render_method_name)(context, data)

        return result

    @property
    def render_method_name(self):
        """
        render_method_name returns method name that renders argument on tag instance
        :return:
        """
        if self._render_method_name:
            return self._render_method_name
        return "render_{}".format(self.name)


class Positional(Argument):
    # is_varargs consumes all positional values (star) including no values
    is_varargs = False

    def __init__(self, is_varargs=False, **kwargs):
        """
        positional argument

        when is_varargs is set, it consumes star args
        :param is_varargs:
        """

        # if no default provided, return blank list
        kwargs['default'] = kwargs.pop('default', [])

        super().__init__(**kwargs)

        # set if we have varargs
        self.is_varargs = is_varargs

    def claim_arguments(self, args: list, kwargs: dict):
        """
        claim_arguments pops values from args and returns value.
        :param args:
        :param kwargs:
        """

        if self.is_varargs:
            value = []
            while True:
                try:
                    value.append(args.pop(0))
                except IndexError:
                    return value

        try:
            value = args.pop(0)
        except IndexError as _:
            raise TemplateSyntaxError("expected positional argument")

        return value

    def get_value(self, context: Context, value):
        """
        returns value from given context
        :param context: context
        :param value: value that contains or is FiterExpression
        """

        # in case there is no value, we should return default
        if not value:
            return self.get_default()

        if self.is_varargs:
            resolved = []
            for item in value:
                try:
                    resolved.append(item.resolve(context, ignore_failures=True))
                except Exception:
                    resolved.append(item)
        else:
            try:
                resolved = value.resolve(context, ignore_failures=True)
            except Exception:
                resolved = value

        return resolved


class Keyword(Argument):

    def claim_arguments(self, args: list, kwargs: dict):
        """
        argument should get args/kwargs that he needs
        :param args:
        :param kwargs:
        """
        return kwargs.pop(self.name, self.get_default())

    def get_value(self, context: Context, value):
        """
        returns value from given context
        :param context: context
        :param value: value that contains or is FiterExpression
        """
        if not value:
            return self.get_default()

        try:
            resolved = value.resolve(context, ignore_failures=True)
        except:
            resolved = value

        return resolved


class KeywordGroup(Argument):
    """
    KeywordGroup of keywords identified by patterns
    """

    # patterns to match group of keyword arguments
    patterns = None

    def __init__(self, patterns, **kwargs):

        super().__init__(**kwargs)

        self.patterns = []

        if utils.is_seq(patterns):
            self.patterns += list(patterns)
        elif isinstance(patterns, str):
            self.patterns.append(patterns)
        else:
            raise TemplateSyntaxError("invalid patterns, expected str/list/tuple, got: {}".format(type(patterns)))

    def claim_arguments(self, args: list, kwargs: dict):
        """
        argument should get args/kwargs that he needs
        :param args:
        :param kwargs:
        """
        values = {}

        globs = [globstr.get(glob) for glob in self.patterns]

        for key in list(kwargs.keys()):
            for g in globs:
                if g.match(key):
                    values[key] = kwargs.pop(key)

        return values
