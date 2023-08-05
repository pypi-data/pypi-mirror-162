
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

import inspect

import django
import django.urls
from django.urls import URLPattern, URLResolver
from packaging.version import Version

django_version_41 = Version(django.get_version()) >= Version('4.1')

if django_version_41:
    from django.contrib.admindocs.utils import lookup_str

url_cache = {}


class Class2URLName(object):
    """Keeps the url_name_cache, scans for views, does the lookups."""

    url_name_cache = None

    @classmethod
    def get_lookup_class_urlname(cls, class_name):
        """Convert a class or class name into a url name."""
        if not cls.url_name_cache:
            cls.generate_url_names_cache()

        if isinstance(class_name, type):
            class_name = '.'.join(
                [inspect.getmodule(class_name).__name__, class_name.__name__])

        if not isinstance(class_name, str):
            raise ValueError('You must supply either a string or a class')

        try:
            url = cls.url_name_cache[class_name]
        except KeyError:
            raise ValueError('Supplied class name "%s" does not match any '
                             'view classes' % (class_name,))

        return url

    @classmethod
    def generate_url_names_cache(cls):
        """Generate the url_name_cache."""
        cls.url_name_cache = cls.parse_urls(
            django.urls.get_resolver().url_patterns)

    @classmethod
    def parse_urls(cls, patterns):
        """Look for urlpatterns for our views."""
        all_patterns = {}
        if isinstance(patterns, list):
            for cur_pattern in patterns:
                all_patterns.update(cls.parse_urls(cur_pattern))

        if isinstance(patterns, URLResolver):
            cur_namespace = patterns.namespace
            all_items = {}
            for cur_pattern in patterns.url_patterns:
                all_items.update(cls.parse_urls(cur_pattern))

            for cur_key, cur_item in all_items.items():
                if not cur_namespace:
                    all_items[cur_key] = '%s' % (cur_item,)
                else:
                    all_items[cur_key] = '%s:%s' % (cur_namespace, cur_item)

            return all_items

        if isinstance(patterns, URLPattern):
            if django_version_41:
                key = lookup_str(patterns)
            else:
                key = patterns.lookup_str

            return {key: patterns.name}

        return all_patterns
