#!/usr/bin/env python
# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is Crash Tests Selenium Tests.
#
# The Initial Developer of the Original Code is
# Mozilla.
# Portions created by the Initial Developer are Copyright (C) 2010
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Dave Hunt <dhunt@mozilla.com>
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

import re
import string
from types import StringType
from distutils.version import Version


class FirefoxVersion(Version):

    """Version numbering for Firefox.

    The following are valid version numbers (shown in the order that
    would be obtained by sorting according to the supplied cmp function):

        3.6       3.6.0  (these two are equivalent)
        4.0
        5.0a1
        5.0(beta)
        5.0b3
        5.0pre
        5.0
        6.0.1

    """

    version_re = re.compile(r'^(\d+) \. (\d+) (\. (\d+))? ((a|b|pre|\(beta\))(\d*))?$', re.VERBOSE)


    def parse (self, vstring):
        match = self.version_re.match(vstring)
        if not match:
            raise ValueError, "invalid version number '%s'" % vstring

        (major, minor, patch, prerelease, prerelease_num) = \
            match.group(1, 2, 4, 6, 7)

        if patch:
            self.version = tuple(map(int, [major, minor, patch]))
        else:
            self.version = tuple(map(int, [major, minor]) + [0])

        if prerelease:
            try:
                self.prerelease = (prerelease, int(prerelease_num))
            except ValueError:
                self.prerelease = (prerelease, None)

        else:
            self.prerelease = None


    def __str__ (self):

        if self.version[2] == 0:
            vstring = string.join(map(str, self.version[0:2]), '.')
        else:
            vstring = string.join(map(str, self.version), '.')

        if self.prerelease:
            vstring += self.prerelease[0]
            if self.prerelease[1]:
                vstring += str(self.prerelease[1])

        return vstring


    def __repr__ (self):
        return "FirefoxVersion ('%s')" % str(self)


    def __cmp__ (self, other):
        if isinstance(other, StringType):
            other = FirefoxVersion(other)

        compare = cmp(self.version, other.version)
        if (compare == 0):              # have to compare prerelease

            # case 1: neither has prerelease; they're equal
            # case 2: self has prerelease, other doesn't; other is greater
            # case 3: self doesn't have prerelease, other does: self is greater
            # case 4: both have prerelease: must compare them!

            if (not self.prerelease and not other.prerelease):
                return 0
            elif (self.prerelease and not other.prerelease):
                return -1
            elif (not self.prerelease and other.prerelease):
                return 1
            elif (self.prerelease and other.prerelease):
                prereleases = ('a', '(beta)', 'b', 'pre')
                prerelease_compare = cmp(prereleases.index(self.prerelease[0]), prereleases.index(other.prerelease[0]))
                if (prerelease_compare == 0):
                    return cmp(self.prerelease[1], other.prerelease[1])
                else:
                    return prerelease_compare

        else:                           # numeric versions don't match --
            return compare              # prerelease stuff doesn't matter
