from __future__ import unicode_literals, print_function, absolute_import
from wrapper_tag.arguments import Keyword, KeywordGroup, Event, Method
from wrapper_tag.rendered import RenderedTag
from wrapper_tag.tag import Tag
from wrapper_tag.utils import parse_bits, is_seq, is_template_debug
from logging import getLogger
from django.core.exceptions import ImproperlyConfigured

# read version from setuptools
__version__ = "0.1.7"

default_app_config = 'wrapper_tag.apps.WrapperTagConfig'

__all__ = (
    'Keyword', 'KeywordGroup', 'Event', 'Method',
    'RenderedTag',
    'Tag',
    'register_tag',
)

logger = getLogger("wrapper_tag")


def register_tag(library, **kwargs):
    """
    Register WrapperTag class
    :param library:
    :param kwargs:
    :return:

    @TODO: update docs for given wrapper tag
    """

    def get_library_name(cls):
        """
        Returns library name
        :param cls:
        :return:
        """
        return repr(cls).split('.')[-2]

    def wrap(cls):
        if not issubclass(cls, Tag) and is_template_debug():
            raise ImproperlyConfigured("Class {} is not WrapperTag instance".format(cls))

        from wrapper_tag import docgen

        cls.__doc__ = docgen.generate(cls)

        # add main library tag
        library.tag(cls.options.start_tag, cls)

        logger.debug("Registered `%s`=>`%s` wrapper tag.", cls.options.start_tag, cls.options.end_tag)

        # # set library_name
        # cls.options.library_name = get_library_name(cls)

        # aliases = []
        # for alias in cls.options.aliases:
        #     if is_seq(alias):
        #         start_tag, end_tag = alias[0], alias[1]
        #     else:
        #         start_tag, end_tag = alias, 'end:{}'.format(alias)
        #     aliases.append({
        #         'start_tag': start_tag,
        #         'end_tag': end_tag,
        #     })
        #
        # doc = cls.gen_doc(aliases=aliases)

        # # register_tag also aliases (if available)
        # for alias in aliases:
        #     new_wrapper_tag_class = type(str('Alias_{}_{}'.format(alias, cls.__name__)), cls.__bases__,
        #                                  dict(cls.__dict__))
        #     new_wrapper_tag_class.options.start_tag = alias['start_tag']
        #     new_wrapper_tag_class.options.end_tag = alias['end_tag']
        #
        #     new_doc = cls.gen_doc(alias_to=cls.options.start_tag)
        #     library.tag(alias['start_tag'], init_outer(new_wrapper_tag_class, doc=new_doc))


        return cls

    return wrap
