from __future__ import absolute_import, print_function, unicode_literals

from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class RenderedTag(object):
    """
    Rendered tag curried string object with data, so we can interact with the data on upper levels
    """
    content = None
    tag = None
    data = None

    def __init__(self, rendered_content, tag_name, **data):
        self.content = rendered_content
        self.tag = tag_name
        self.data = data

    def __str__(self):
        """
        Return rendered content
        :return:
        """
        return self.content

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        return self.data[attr]
