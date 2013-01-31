#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Copyright (c) 2012 dput authors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from dput.profile import parse_overrides
from dput.exceptions import DputConfigurationError

def test_parse_overrides():
    test_cases = [
        ({'foo': [['bar']]},
            ['foo=bar']),
        ({'foo': [None]},
            ['-foo']),
        ({'+foo': [['bar']]},
            ['+foo=bar']),
        ({'foo': [None, ['1']]},
            ['-foo', 'foo=1']),
        ({'foo': {'bar': {'baz': [['paultag.is.a.god']]}}},
            ['foo.bar.baz=paultag.is.a.god']),
        ({'foo': {'bar': [['1'], ['2'], ['3']]}, 'foo2': [['4']]},
            ['foo.bar=1', 'foo.bar=2', 'foo.bar=3', 'foo2=4']),
        ({'foo': {'bar': [['True=True'], ['foo=False', 'obj2']]},
          'foo2': [['bar']]},
            ['foo.bar      =     "True=True"', "foo.bar='foo'=False 'obj2'",
             'foo2=bar'])
     ]

    bad_test_cases = [
                      (None, ['invalid']),
                      (None, ['foo=bar', 'foo=bar', 'foo.bar=bar']),
                      (None, ['foo.bar=1', 'foo.bar.baz=1'])
    ]

    for (expectation, case) in test_cases:
        print(parse_overrides(case))
        assert(expectation == parse_overrides(case))

    for (expectation, case) in bad_test_cases:
        try:
            parse_overrides(case)
            raise Exception("Bad test case: %s" % (case))
        except DputConfigurationError:
            pass
