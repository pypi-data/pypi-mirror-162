
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
import pytest

from django_auto_url.urls import reverse_classname, reverse_classname_lazy
from django_auto_url.tests.views import test_views
from django_auto_url.tests.factories import StringItemFactory
from django_auto_url.tests.utils import assert_stringitem


def test_simple_access(selenium, live_server):
    """Simple test for reverse_classname."""
    selenium.open(live_server.url +
                  reverse_classname(
                      test_views.EmptyView))

    selenium.assert_text('Hello')


def test_simple_access_lazy(selenium, live_server):
    """Simple test for reverse_classname_lazy."""
    selenium.open(live_server.url +
                  str(reverse_classname_lazy(
                      test_views.EmptyView)))

    selenium.assert_text('Hello')


def test_index(selenium, live_server):
    """Test index view."""
    selenium.open(live_server.url)
    selenium.assert_text('Index')


def test_kwargs(selenium, live_server):
    """Test with kwargs."""
    my_int = 42
    my_string = 'Oh Hello!'
    my_bool = True

    selenium.open(live_server +
                  reverse_classname(
                      test_views.KwargsView,
                      kwargs={'int': my_int,
                              'string': my_string,
                              'bool': my_bool}
                  ))

    with pytest.raises(RuntimeError, match='args and kwargs not allowed if '
                                           'return_url_name=True.'):
        reverse_classname(
            test_views.KwargsView,
            return_url_name=True,
            kwargs={'int': my_int,
                    'string': my_string,
                    'bool': my_bool}
        )

    selenium.assert_text('Int: ' + str(my_int))
    selenium.assert_text('String: ' + my_string)
    selenium.assert_text('Bool: ' + str(my_bool))

    my_int = 22
    my_string = 'Blabla'
    my_bool = False

    selenium.open(live_server +
                  reverse_classname(
                      test_views.KwargsView,
                      args=[my_string,
                            my_int,
                            my_bool]
                  ))

    selenium.assert_text('Int: ' + str(my_int))
    selenium.assert_text('String: ' + my_string)
    selenium.assert_text('Bool: ' + str(my_bool))

    with pytest.raises(RuntimeError, match='args and kwargs not allowed if '
                                           'return_url_name=True.'):
        reverse_classname(
            test_views.KwargsView,
            return_url_name=True,
            args=[my_string,
                  my_int,
                  my_bool]
        )


def test_links(selenium, live_server):
    """Test with links in template."""
    selenium.open(live_server +
                  reverse_classname(
                      test_views.WithLinksView)
                  )
    selenium.click('#index_link')
    selenium.assert_text('Index')
    selenium.open(live_server +
                  reverse_classname(
                      test_views.WithLinksView)
                  )
    selenium.click('#kwargs_link')
    selenium.assert_text('Int: ' + str(32))
    selenium.assert_text('String: ' + 'New String')
    selenium.assert_text('Bool: ' + str(False))

    selenium.open(live_server +
                  reverse_classname(
                      test_views.WithLinksView)
                  )
    selenium.click('#kwargs_default_link')
    selenium.assert_text('Int: ' + str(33))
    selenium.assert_text('String: ' + 'New New String')
    selenium.assert_text('Bool: ' + str(True))


def test_kwargs_with_defaults(selenium, live_server):
    """Test with default kwargs."""
    my_int = 22
    my_string = 'Blabla'
    my_bool = False

    default_int = 33
    default_bool = True

    selenium.open(live_server +
                  reverse_classname(
                      test_views.KwargsViewWithDefaults,
                      kwargs={'int': my_int,
                              'string': my_string,
                              'bool': my_bool}
                  ))

    selenium.assert_text('Int: ' + str(my_int))
    selenium.assert_text('String: ' + my_string)
    selenium.assert_text('Bool: ' + str(my_bool))

    selenium.open(live_server + reverse_classname(
        test_views.KwargsViewWithDefaults,
        kwargs={'string': my_string}
    ))

    selenium.assert_text('Int: ' + str(default_int))
    selenium.assert_text('String: ' + my_string)
    selenium.assert_text('Bool: ' + str(default_bool))

    selenium.open(live_server + reverse_classname(
        test_views.KwargsViewWithDefaults,
        kwargs={'int': my_int,
                'string': my_string}
    ))

    selenium.assert_text('Int: ' + str(my_int))
    selenium.assert_text('String: ' + my_string)
    selenium.assert_text('Bool: ' + str(default_bool))


def test_view_with_args_templatetag(selenium, live_server, settings):
    """Test if args in templatetag are forbidden."""
    settings.DEBUG = True
    selenium.open(live_server +
                  reverse_classname(
                      test_views.WithInvalidArgInTemplateTagView))

    selenium.assert_text('Only keyword arguments are '
                         'allowed when using the '
                         '"url_from_class" template tag.')


def test_access_suburl(selenium, live_server):
    """Test whether suburls work."""
    selenium.open(live_server + reverse_classname(
        'django_auto_url.tests.views.test_sub_views.NormalSubView'
    ))

    selenium.assert_text('Hello')


def test_local_reverse(selenium, live_server):
    """Test local reverse."""
    selenium.open(live_server + reverse_classname(
        test_views.WithLinkTargetFromContextView
    ))

    selenium.click('#link')

    selenium.assert_text('Hello')


@pytest.mark.django_db
def test_pk_slug(selenium, live_server):
    """Test pk and slug."""
    all_items = StringItemFactory.create_batch(10)

    selenium.open(live_server.url)
    for cur_item in all_items:
        selenium.open(live_server +
                      reverse_classname(test_views.StringItemFromPK,
                                        kwargs={'pk': cur_item.pk}))

        assert_stringitem(selenium, cur_item)

        selenium.open(live_server +
                      reverse_classname(test_views.StringItemFromCustomPK,
                                        kwargs={'test_pk': cur_item.pk}))

        assert_stringitem(selenium, cur_item)

        selenium.open(live_server +
                      reverse_classname(test_views.StringItemFromSlug,
                                        kwargs={'slug': cur_item.test_slug}))

        assert_stringitem(selenium, cur_item)
