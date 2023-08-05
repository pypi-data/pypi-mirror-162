
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

from django_auto_url.urls import reverse_classname
from django_auto_url.tests.views.test_bad_index_view import BadIndexView
import pytest


@pytest.mark.urls('django_auto_url.tests.urls_for_bad_index_tests')
def test_invalid_index(selenium, live_server):
    """Test that an invalid index view raises an exception."""
    with pytest.raises(RuntimeError, match='An Index View cannot '
                                           'have kwargs.'):
        selenium.open(live_server + reverse_classname(BadIndexView))
