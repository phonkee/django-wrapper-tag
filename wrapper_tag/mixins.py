from django.template import Template, TemplateDoesNotExist
from django.template.loader import get_template


class TemplateMixin:

    template = None
    template_name = None

    def __init__(self, template=None, template_name=None):
        self.template = template
        self.template_name = template_name

    def get_template(self) -> Template:
        """
        get_template returns parsed template
        :return:
        """
        if self.template:
            return Template(self.template)
        elif self.template_name:
            return get_template(self.template_name)

        raise TemplateDoesNotExist("no template provided")