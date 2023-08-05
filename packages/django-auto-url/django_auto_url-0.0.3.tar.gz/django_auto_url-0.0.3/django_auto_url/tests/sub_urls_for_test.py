
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

from django_auto_url.urls import get_urls_from_module
from django_auto_url.tests.views import test_sub_views

app_name = 'test_for_autourl'

urlpatterns = get_urls_from_module(test_sub_views)
