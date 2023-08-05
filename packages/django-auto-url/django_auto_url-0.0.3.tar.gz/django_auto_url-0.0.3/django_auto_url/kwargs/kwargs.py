
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


class kwarg(object):
    """Base class for Keyword Arguments.

    Attributes
    ----------
    regex : str
        The regular expression for this type.

    name : str
        The name of this keyword argument.

    default
        The default value for this keyword argument. None if no default.
    """

    regex = None

    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def get_regex(self):
        """Return the regular expression for this Keyword Argument.

        Returns
        -------
        str
            The generated regular expression.
        """
        return r'(?P<%s>%s)' % (self.name, self.regex)


class string(kwarg):
    """String Keyword Argument."""

    regex = '.*'


class int(kwarg):
    """Int Keyword Argument."""

    regex = '[0-9]*'


class bool(kwarg):
    """Bool Keyword Argument."""

    regex = 'True|False'
