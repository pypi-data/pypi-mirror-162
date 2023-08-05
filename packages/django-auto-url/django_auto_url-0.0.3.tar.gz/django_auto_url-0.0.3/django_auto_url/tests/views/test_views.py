
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

from django.views.generic import TemplateView, DetailView

from django_auto_url import kwargs
from django_auto_url.mixins import AutoUrlMixin
from django_auto_url.urls import reverse_local_classname
from django_auto_url.tests import models


class EmptyView(AutoUrlMixin, TemplateView):
    """Most generic Test View."""

    template_name = 'generic.html'


class IndexView(AutoUrlMixin, TemplateView):
    """View to test is_index."""

    is_index = True
    template_name = 'index.html'


class KwargsView(AutoUrlMixin, TemplateView):
    """View to test Kwargs."""

    template_name = 'use_kwargs.html'
    url_kwargs = [kwargs.string('string'),
                  kwargs.int('int'),
                  kwargs.bool('bool')]


class KwargsViewWithDefaults(AutoUrlMixin, TemplateView):
    """View to test Kwargs with defaults."""

    template_name = 'use_kwargs.html'
    url_kwargs = [kwargs.string('string'),
                  kwargs.int('int', 33),
                  kwargs.bool('bool', True)]


class WithLinksView(AutoUrlMixin, TemplateView):
    """View that has a template with links."""

    template_name = 'with_links.html'


class WithInvalidArgInTemplateTagView(AutoUrlMixin,
                                      TemplateView):
    """View that has a template with invalid links."""

    template_name = 'with_args_link.html'


class WithLinkTargetFromContextView(AutoUrlMixin,
                                    TemplateView):
    """View that has a link defining the target from the context."""

    template_name = 'link_target_from_context.html'
    extra_context = {
        'link_target': reverse_local_classname('EmptyView')
    }


class StringItemFromPK(AutoUrlMixin, DetailView):
    """View displaying a StringItem."""

    template_name = 'string_object.html'
    model = models.StringItem


class StringItemFromCustomPK(AutoUrlMixin, DetailView):
    """View displaying a StringItem using custom PK field."""

    template_name = 'string_object.html'
    model = models.StringItem
    pk_url_kwarg = 'test_pk'


class StringItemFromSlug(AutoUrlMixin, DetailView):
    """View displaying a StringItem using the slug field."""

    template_name = 'string_object.html'
    model = models.StringItem
    pk_url_kwarg = None
    slug_field = 'test_slug'
