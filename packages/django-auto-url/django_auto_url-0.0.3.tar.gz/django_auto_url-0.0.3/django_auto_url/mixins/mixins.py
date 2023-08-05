
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

from django.urls import re_path

from django_auto_url import kwargs


class AutoUrlMixin:
    """Mixin for automatic URL url creation.

    Include this Mixin in your :class:`~django.views.generic.base.View`
    to have a urlpattern automatically
    generated when this surrounding package is scanned with
    :func:`~django_auto_url.urls.get_urls_from_module`.

    Attributes
    ----------
    url_path_name : str, optional
        If set, this is the string that appears in the actual URL. Otherwise
        the class name is used.

    url_django_name : str, optional
        If set, this is the name of the route in django. Otherwise
        the class name is used.

    is_index : bool
        Set to :code:`True` if this is an index view.

    url_kwargs : list of :class:`~django_auto_url.kwargs.kwargs.kwarg`
        The list of Keyword Arguments for this view.

    url_ignore_pk : bool
        If the :class:`~django.views.generic.base.View` includes a
        :code:`slug_url_kwarg` or :code:`pk_url_kwarg` class attribute
        (like the :class:`~django.views.generic.detail.DetailView`),
        a keyword argument for the Primary Key or the Slug is included
        automatically. Set this to :code:`False` if this is not what you want.
    """

    url_path_name = None
    url_kwargs = None
    url_django_name = None
    is_index = False
    url_ignore_pk = False

    @classmethod
    def get_url_path_name(cls):
        """Return the url_path_name."""
        if cls.url_path_name:
            return cls.url_path_name
        else:
            return cls.__name__

    @classmethod
    def get_url_kwargs(cls):
        """Return the Keyword Arguments."""
        url_kwargs = cls.url_kwargs
        if not url_kwargs and hasattr(cls, 'pk_url_kwarg') \
                and not cls.url_ignore_pk and cls.pk_url_kwarg is not None:
            if cls.pk_url_kwarg == 'pk':
                url_kwargs = [kwargs.int('pk')]
            else:
                url_kwargs = [
                    kwargs.string(cls.pk_url_kwarg)]

        if not url_kwargs and hasattr(cls, 'slug_url_kwarg') \
                and not cls.url_ignore_pk and cls.slug_url_kwarg is not None:
            url_kwargs = [
                kwargs.string(cls.slug_url_kwarg)]

        return url_kwargs

    @classmethod
    def get_url_django_name(cls):
        """Return the django url name."""
        if cls.url_django_name:
            return cls.url_django_name
        else:
            return cls.__name__

    @classmethod
    def get_url(cls):
        """
        Generate and return the :class:`~django.urls.resolvers.URLResolver`s.

        Returns
        -------
        list of :class:`~django.urls.resolvers.URLResolver`
        """
        if cls.is_index and cls.url_kwargs:
            raise RuntimeError('An Index View cannot have kwargs.')

        if cls.is_index:
            url_part = r'^$'
            return [re_path(url_part, cls.as_view(),
                            name=cls.get_url_django_name())]
        else:
            return cls._create_url(cls.get_url_path_name(),
                                   cls.get_url_kwargs(),
                                   cls.get_url_django_name())

    @classmethod
    def _create_url(cls, path_name, url_kwargs, django_name):
        url_list = []

        url_part = r'^%s/' % (path_name,)

        if url_kwargs:
            if url_kwargs[-1].default is not None:
                new_url_kwargs = url_kwargs[0:-1]
                url_list = cls._create_url(
                    path_name, new_url_kwargs, django_name) + url_list

            for cur_kwarg in url_kwargs:
                url_part = url_part + r'%s/' % (cur_kwarg.get_regex())

        url_part = url_part + r'$'

        url_list.insert(0, re_path(url_part, cls.as_view(), name=django_name))

        return url_list

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):  # noqa: D102
        total_n_args = len(args) + len(kwargs)
        if self.url_kwargs:
            for idx_kwarg, cur_kwarg in enumerate(self.url_kwargs):
                if idx_kwarg >= total_n_args and \
                        cur_kwarg.name not in kwargs:
                    kwargs[cur_kwarg.name] = cur_kwarg.default

        return super().dispatch(request, *args, **kwargs)
