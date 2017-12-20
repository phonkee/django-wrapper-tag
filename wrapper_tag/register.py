from django.core.exceptions import ImproperlyConfigured
from django.template.library import Library

from . import utils


def register_tag(library: Library):
    """
    Register WrapperTag class
    :param library: template library to register tag to
    :return:
    """

    def wrap(cls):
        from wrapper_tag.tags import Tag
        if not issubclass(cls, Tag) and utils.is_template_debug():
            raise ImproperlyConfigured("Class {} is not WrapperTag instance".format(cls))

        # here is a place to generate documentation for tag

        # add main library tag
        library.tag(cls._meta.start_tag, cls.compile)

        return cls

    return wrap
