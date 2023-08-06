import random
import string

from django import template
from django.shortcuts import reverse

from bs4 import BeautifulSoup

register = template.Library()


@register.filter
def add_class_to_el(value: str, arg: str) -> str:
    """Add a CSS class to every occurence of an element type.

    :Example:

    .. code-block::

        {{ mymodel.myhtmlfield|add_class_to_el:"ul,browser-default" }}
    """
    el, cls = arg.split(",")
    soup = BeautifulSoup(value, "html.parser")

    for el in soup.find_all(el):
        el["class"] = el.get("class", []) + [cls]

    return str(soup)


@register.simple_tag
def generate_random_id(prefix: str, length: int = 10) -> str:
    """Generate a random ID for templates.

    :Example:

    .. code-block::

        {% generate_random_id "prefix-" %}
    """
    return prefix + "".join(
        random.choice(string.ascii_lowercase) for i in range(length)  # noqa: S311
    )


@register.simple_tag(takes_context=True)
def absolute_url(context, view_name, *args, **kwargs):
    request = context["request"]
    return request.build_absolute_uri(reverse(view_name, args=args, kwargs=kwargs))
