"""
@author 'Peter Vrba <phonkee@phonkee.eu>'
"""

import stringcase

from wrapper_tag import mixins


class Options(mixins.TemplateMixin):
    """
    Options for tag.
    We store following information
    * start_tag
    * end_tag
    * namespace - for adding prefix and colon
    """
    as_var_only = False
    start_tag = None
    end_tag = None
    namespace = ""

    def __init__(self, meta: object, cls_name: str):
        """
        Create new options instance.
        :type meta: class Meta (as known from django models/forms)
        :type cls_name: basestring class name
        """
        kwargs = {
            'template': getattr(meta, 'template', None),
            'template_name': getattr(meta, 'template_name', None),
        }

        super().__init__(**kwargs)
        self.namespace = self._get_namespace(meta)
        self.start_tag = self._get_start_tag(meta, cls_name)
        self.end_tag = self._get_end_tag(meta, self.start_tag)
        self.as_var_only = bool(getattr(meta, 'as_var_only', False))

    def _get_start_tag(self, meta: object, cls_name: str) -> str:
        """
        _get_start_tag extracts start_tag from met object or from class name
        :param meta:
        :return:
        """
        start_tag = getattr(meta, "start_tag", None)

        # start_tag not provided, create one from tag class name
        if start_tag is None:

            start_tag = cls_name

            # try to remove trailing "Tag" "tag"
            if len(cls_name) > 3:
                if cls_name[-3:].lower() == "tag":
                    start_tag = cls_name[:-3]

        start_tag = stringcase.snakecase(start_tag)

        if self.namespace is not None:
            start_tag = "{}:{}".format(self.namespace, start_tag)

        return start_tag

    def _get_end_tag(self, meta: object, start_tag: str) -> str:
        """
        _get_end_tag returns end tag from given meta options, or derives one from start_tag
        :param meta: class Meta from tag
        :param start_tag: start tag
        :return:
        """
        return getattr(meta, 'end_tag', "end:{}".format(start_tag))

    def _get_namespace(self, meta):
        """
        _get_namespace returns namespace if provided
        :param meta:
        :return:
        """
        namespace = getattr(meta, 'namespace', None)
        if namespace is not None:
            namespace = stringcase.snakecase(namespace)

        return namespace
