
# django_auto_url - Automagic URLs for Django
# Copyright (C) 2019 Thomas Hartmann <thomas.hartmann@th-ht.de>
#
# This file is part of django_auto_url.
#
# django_auto_url is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django_auto_url is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django_auto_url.  If not, see <http://www.gnu.org/licenses/>.

from django import template
from django.template import TemplateSyntaxError
from django.template.base import kwarg_re
from django.template.defaulttags import URLNode

from django_auto_url.utils.class2urlname import Class2URLName

register = template.Library()


@register.tag
def url_from_class(parser, token):
    """Template tag to resolve URL from class."""
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError(
            "'%s' takes at least one argument, the name of a url()." % bits[0])

    tmp_name = "'%s'" % \
               (Class2URLName.get_lookup_class_urlname(bits[1][1:-1]),)
    viewname = parser.compile_filter(tmp_name)

    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    if args:
        raise template.TemplateSyntaxError('Only keyword arguments are '
                                           'allowed when using the '
                                           '"url_from_class" template tag.')

    return URLNode(viewname, args, kwargs, asvar)
