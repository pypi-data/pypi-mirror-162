
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

import django.urls
from django_auto_url.utils.lazy import lazy

from django_auto_url.mixins import AutoUrlMixin
from django_auto_url.utils.class2urlname import url_cache, Class2URLName


def get_urls_from_module(module):
    """Scan a package and return the urlpatterns.

    This function scans the module for all subclasses of
    :class:`~django_auto_url.mixins.mixins.AutoUrlMixin`,  generates
    a :class:`~django.urls.resolvers.URLResolver` for each of them
    and returns a list that you can feed directly to :code:`urlpatterns`.

    Parameters
    ----------
    module : module
        The module to scan.

    Returns
    -------
    list of :class:`~django.urls.resolvers.URLResolver`

    Example
    -------
    Assuming, you have your views defined in the module
    :code:`my_app.views`, this is, how your :code:`urls.py` would look like:

    >>> from my_app import views
    >>> from django_auto_url.urls import get_urls_from_module
    >>>
    >>> urlpatterns = get_urls_from_module(views)

    """
    package_classes = [mod[1] for mod in
                       inspect.getmembers(module, inspect.isclass) if
                       mod[1].__module__ == module.__name__]
    url_classes = [cls for cls in package_classes if
                   issubclass(cls, AutoUrlMixin)]

    all_urls = []
    for cur_class in url_classes:
        url_cache['.'.join([inspect.getmodule(cur_class).__name__,
                            cur_class.__name__])] = cur_class
        rval = cur_class.get_url()
        if isinstance(rval, list):
            all_urls.extend(rval)
        else:
            all_urls.append(rval)

    return all_urls


def reverse_classname(class_name, return_url_name=False,
                      args=None, kwargs=None):  # noqa: D207, D301
    """Get the URL for a View.

    Converts a :class:`~django.views.generic.base.View` into its URL or
    the django url name.

    Parameters
    ----------
    class_name : str or subclass of \
:class:`~django_auto_url.mixins.mixins.AutoUrlMixin`
        The :class:`~django.views.generic.base.View` to reverse. You can either
        provide the class directly or a string with the full module path.
    return_url_name : bool, optional
        If set to :code:`True`, return the django url name and not the
        final URL.
    args : list, optional
        The positional arguments for the view.
    kwargs : dict, optional
        The keyword arguments for the view.

    Returns
    -------
    str
        The URL or the django url name.

    """
    url_name = Class2URLName.get_lookup_class_urlname(class_name)
    if return_url_name:
        if args or kwargs:
            raise RuntimeError('args and kwargs not '
                               'allowed if return_url_name=True.')
        return url_name
    else:
        return django.urls.reverse(url_name, args=args, kwargs=kwargs)


def reverse_classname_lazy(class_name, return_url_name=False,
                           args=None, kwargs=None):
    """Lazy version of :func:`~django_auto_url.urls.urls.reverse_classname`.

    Instead of doing the reverse instantly, it is done, when the result is
    actually needed. This will help you when you need to specify a URL
    in a class attribute. The non-lazy version would instantly try to find
    the URL for the view, even if the view has not been declared yet
    (for instance, because it is declared later in the same file or in a
    different one).

    Arguments and return values are exactly the same as
    :func:`~django_auto_url.urls.urls.reverse_classname`.
    """
    r_lazy = lazy(reverse_classname, str)
    return r_lazy(class_name, return_url_name, args, kwargs)


def reverse_local_classname(class_name,
                            return_url_name=False,
                            args=None,
                            kwargs=None,
                            lazy=True):  # noqa: D207, D301
    """Get the URL of a view declared in the same module.

    Basically does the same as
    :func:`~django_auto_url.urls.urls.reverse_classname` but you do not
    need to specify the full module path to the view. The class name is
    enough.

    Parameters
    ----------
    class_name : str or subclass of \
:class:`~django_auto_url.mixins.mixins.AutoUrlMixin`
        The :class:`~django.views.generic.base.View` to reverse. You can either
        provide the class directly or a string with the full module path.
    return_url_name : bool, optional
        If set to :code:`True`, return the django url name and not the
        final URL.
    args : list, optional
        The positional arguments for the view.
    kwargs : dict, optional
        The keyword arguments for the view.
    lazy : bool, optional
        Determines whether the evaluation should be lazy.

    Returns
    -------
    str
        The URL or the django url name.
    """
    cur_frame = inspect.currentframe()
    class_name = '.'.join(
        [cur_frame.f_back.f_locals['__module__'], class_name])

    if lazy:
        return reverse_classname_lazy(class_name, return_url_name,
                                      args, kwargs)
    else:
        return reverse_classname(class_name, return_url_name,
                                 args, kwargs)
