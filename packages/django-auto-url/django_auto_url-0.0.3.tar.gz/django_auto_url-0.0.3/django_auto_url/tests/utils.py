
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


def assert_stringitem(selenium, cur_item):
    """Assert a Stringitem."""
    selenium.assert_text('pk: %d' % (cur_item.pk,))
    selenium.assert_text('test_pk: %d' % (cur_item.test_pk,))
    selenium.assert_text('test_slug: %s' % (cur_item.test_slug,))
    selenium.assert_text('test_string: %s' % (cur_item.test_string,))
