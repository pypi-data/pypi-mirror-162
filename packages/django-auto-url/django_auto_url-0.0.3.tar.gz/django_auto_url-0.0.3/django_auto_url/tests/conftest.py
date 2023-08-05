
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
import seleniumbase
from django_auto_url.utils.class2urlname import Class2URLName


@pytest.fixture(scope='session', autouse=True)
def init_tests(tmpdir_factory):
    """General init fixture for all pytests."""
    # settings.STATIC_ROOT = str(tmpdir_factory.mktemp('static'))
    # call_command('collectstatic', interactive=False)
    yield


@pytest.fixture(scope='module', autouse=True)
def init_tests_module():
    Class2URLName.url_name_cache = None
    yield


@pytest.fixture(scope='module')
def selenium():
    """Fixture returning a seleniumbase."""
    this_sel = seleniumbase.BaseCase('__init__')
    this_sel.setUp()
    yield this_sel
    this_sel.tearDown()
