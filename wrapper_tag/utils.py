"""
@author 'Peter Vrba <phonkee@phonkee.eu>'
"""
import inspect

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateSyntaxError
from django.template.base import token_kwargs


def _uniqueid():
    """
    generator that yields ids
    :return:
    """
    initial = 1
    while True:
        yield "id_{}".format(initial)
        initial += 1


# unique_id generator instance
unique_id = _uniqueid()


def is_seq(target):
    """
    is_seq returns whether is argument list/tuple/iterable
    :param target:
    :return:
    """
    if isinstance(target, (list, tuple)):
        return True
    return False


def is_template_debug() -> bool:
    """
    is_template_debug returns whether django template debug is enabled
    :return:
    """
    return getattr(settings, 'TEMPLATE_DEBUG', False)


def parse_bits(parser, bits, name):
    """
    Taken from django code and enhanced (params accept also wildcard on the end of string

    Parses bits for template tag helpers (simple_tag, include_tag and
    assignment_tag), in particular by detecting syntax errors and by
    extracting positional and keyword arguments.
    :param name:
    :param bits:
    :param parser:
    """
    args = []
    kwargs = {}
    for bit in bits:
        # First we try to extract a potential kwarg from the bit
        kwarg = token_kwargs([bit], parser)
        if kwarg:
            # The kwarg was successfully extracted
            param, value = list(kwarg.items())[0]
            if param in kwargs:
                # The keyword argument has already been supplied once
                raise TemplateSyntaxError(
                    "'%s' received multiple values for keyword argument '%s'" %
                    (name, param))
            else:
                # All good, record the keyword argument
                kwargs[str(param)] = value
        else:
            if kwargs:
                raise TemplateSyntaxError(
                    "'%s' received some positional argument(s) after some "
                    "keyword argument(s)" % name)
            else:
                # Record the positional argument
                args.append(parser.compile_filter(bit))

    return args, kwargs


def verify_func_signature(func, *args):
    """
    verify signature of function
    :param func:
    :return:
    """
    sig: inspect.Signature = inspect.signature(func)
    params = [str(v) for k, v in sig.parameters.items() if k != "self"]
    str_repr = ", ".join(params)
    expect = ", ".join(args)

    if str_repr != expect:
        raise ImproperlyConfigured(
            "Method `{}` should have signature: `def ({}): pass` got `def({})`".format(func.__name__, expect,
                                                                                       str_repr))
