"""
@author 'Peter Vrba <phonkee@phonkee.eu>'
"""


class RenderedTag(dict):
    """
    RenderedTag represents rendered tag along with ability to store data.
    """
    content = None
    tag = None

    def __init__(self, rendered_content, tag_name, **data):
        self.content = rendered_content
        self.tag = tag_name
        super().__init__(**data)

    def __str__(self):
        """
        Return rendered content
        :return:
        """
        return self.content

    def __repr__(self):
        """
        Return rendered content
        :return:
        """
        return self.content

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        return self[attr]

    def __nonzero__(self):
        return str(self).strip() != ''
