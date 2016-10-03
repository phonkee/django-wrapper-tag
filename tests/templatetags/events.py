import six
from django import template

import wrapper_tag

register = template.Library()


class MyEvent(wrapper_tag.Keyword):

    def contribute_to_class(self, tag_cls, name):
        super(MyEvent, self).contribute_to_class(tag_cls, name)

        # bound to signal
        tag_cls.on_rendered_tag.connect(self.on_rendered_tag, dispatch_uid="events")

    def on_rendered_tag(self, sender, rendered_tag, data, context, **kwargs):
        """
        Collect all events and expose them to rendered tag
        :param sender: tag class
        :param rendered_tag: rendered tag instance
        :param data: tag data
        :param context: render context
        :return:
        """
        events = {}
        for _, argument in six.iteritems(sender.arguments):

            value = data.get(argument.name)
            if not value:
                continue
            events[argument.name] = value

        # store events
        rendered_tag['events'] = events


@wrapper_tag.register_tag(register)
class ExampleRenderedTag(wrapper_tag.Tag):
    on_click = MyEvent(default="hola")
    on_release = MyEvent()
    on_boom = MyEvent()

    class Meta:
        start_tag = "ex_rendered"
        template = "<div>{{ content }}</div>"
