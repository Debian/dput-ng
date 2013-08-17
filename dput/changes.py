# -*- coding: utf-8 -*-
#
#   changes.py — .changes file handling class
#
#   This file was originally part of debexpo
#    https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2012 Arno Töll <arno@debian.org>
#   Copyright © 2012 Paul Tagliamonte <paultag@debian.org>
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use,
#   copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following
#   conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.
"""
This code deals with the reading and processing of Debian .changes files. This
code is copyright (c) Jonny Lamb, and is used by dput, rather then created as
a result of it. Thank you Jonny.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

import sys
import os.path
import hashlib
from debian import deb822

from dput.core import logger
from dput.util import run_command
from dput.exceptions import ChangesFileException


class Changes(object):
    """
    Changes object to help process and store information regarding Debian
    .changes files, used in the upload process.
    """

    def __init__(self, filename=None, string=None):
        """
        Object constructor. The object allows the user to specify **either**:

        #. a path to a *changes* file to parse
        #. a string with the *changes* file contents.

        ::

        a = Changes(filename='/tmp/packagename_version.changes')
        b = Changes(string='Source: packagename\\nMaintainer: ...')

        ``filename``
            Path to *changes* file to parse.

        ``string``
            *changes* file in a string to parse.
        """
        if (filename and string) or (not filename and not string):
            raise TypeError

        if filename:
            self._absfile = os.path.abspath(filename)
            self._data = deb822.Changes(open(filename))
        else:
            self._data = deb822.Changes(string)

        if len(self._data) == 0:
            raise ChangesFileException('Changes file could not be parsed.')
        if filename:
            self.basename = os.path.basename(filename)
        else:
            self.basename = None
        self._directory = ""

        self.is_python3 = False
        if sys.version_info[0] >= 3:
            self.is_python3 = True

    def get_filename(self):
        """
        Returns the filename from which the changes file was generated from.
        Please do note this is just the basename, not the entire full path, or
        even a relative path. For the absolute path to the changes file, please
        see :meth:`get_changes_file`.
        """
        return self.basename

    def get_changes_file(self):
        """
        Return the full, absolute path to the changes file. For just the
        filename, please see :meth:`get_filename`.
        """
        return os.path.join(self._directory, self.get_filename())

    def get_files(self):
        """
        Returns a list of files referenced in the changes file, such as
        the .dsc, .deb(s), .orig.tar.gz, and .diff.gz or .debian.tar.gz.
        All strings in the array will be absolute paths to the files.
        """
        return [os.path.join(self._directory, z['name'])
                for z in self._data['Files']]

    def __getitem__(self, key):
        """
        Returns the value of the rfc822 key specified.

        ``key``
            Key of data to request.
        """
        return self._data[key]

    def __contains__(self, key):
        """
        Returns whether the specified RFC822 key exists.

        ``key``
            Key of data to check for existence.
        """
        return key in self._data

    def get(self, key, default=None):
        """
        Returns the value of the rfc822 key specified, but defaults
        to a specific value if not found in the rfc822 file.

        ``key``
            Key of data to request.

        ``default``
            Default return value if ``key`` does not exist.
        """
        return self._data.get(key, default)

    def get_component(self):
        """
        Returns the component of the package.
        """
        return self._parse_section(self._data['Files'][0]['section'])[0]

    def get_priority(self):
        """
        Returns the priority of the package.
        """
        return self._parse_section(self._data['Files'][0]['priority'])[1]

    def get_section(self):
        """
        Returns the section of the package.
        """
        return self._parse_section(self._data['Files'][0]['section'])[1]

    def get_dsc(self):
        """
        Returns the name of the .dsc file.
        """
        for item in self.get_files():
            if item.endswith('.dsc'):
                return item

    def get_diff(self):
        """
        Returns the name of the .diff.gz file if there is one, otherwise None.
        """
        for item in self.get_files():
            if item.endswith('.diff.gz') or item.endswith('.debian.tar.gz'):
                return item

        return None

    def get_pool_path(self):
        """
        Returns the path the changes file would be
        """
        return self._data.get_pool_path()

    def get_package_name(self):
        """
        Returns the source package name
        """
        return self.get("Source")

    def _parse_section(self, section):
        """
        Works out the component and section from the "Section" field.
        Sections like `python` or `libdevel` are in main.
        Sections with a prefix, separated with a forward-slash also show the
        component.
        It returns a list of strings in the form [component, section].

        For example, `non-free/python` has component `non-free` and section
        `python`.

        ``section``
        Section name to parse.
        """
        if '/' in section:
            return section.split('/')
        else:
            return ['main', section]

    def set_directory(self, directory):
        if directory:
            self._directory = directory
        else:
            self._directory = ""

    def validate(self, check_hash="sha1", check_signature=True):
        """
        See :meth:`validate_checksums` for ``check_hash``, and
        :meth:`validate_signature` if ``check_signature`` is True.
        """
        self.validate_checksums(check_hash)
        if check_signature:
            self.validate_signature(check_signature)
        else:
            logger.info("Not checking signature")

    def validate_signature(self, check_signature=True):
        """
        Validate the GPG signature of a .changes file.

        Throws a :class:`dput.exceptions.ChangesFileException` if there's
        an issue with the GPG signature. Returns the GPG key ID.
        """
        gpg_path = "gpg"

        (gpg_output, gpg_output_stderr, exit_status) = run_command([
            gpg_path, "--status-fd", "1", "--verify",
            "--batch", self.get_changes_file()
        ])

        if exit_status == -1:
            raise ChangesFileException(
                "Unknown problem while verifying signature")

        # contains verbose human readable GPG information
        if self.is_python3:
            gpg_output_stderr = str(gpg_output_stderr, encoding='utf8')
        print(gpg_output_stderr)

        if self.is_python3:
            gpg_output = gpg_output.decode(encoding='UTF-8')

        if gpg_output.count('[GNUPG:] GOODSIG'):
            pass
        elif gpg_output.count('[GNUPG:] BADSIG'):
            raise ChangesFileException("Bad signature")
        elif gpg_output.count('[GNUPG:] ERRSIG'):
            raise ChangesFileException("Error verifying signature")
        elif gpg_output.count('[GNUPG:] NODATA'):
            raise ChangesFileException("No signature on")
        else:
            raise ChangesFileException(
                "Unknown problem while verifying signature"
            )

        key = None
        for line in gpg_output.split("\n"):
            if line.startswith('[GNUPG:] VALIDSIG'):
                key = line.split()[2]
        return key

    def validate_checksums(self, check_hash="sha1"):
        """
        Validate checksums for a package, using ``check_hack``'s type
        to validate the package.

        Valid ``check_hash`` types:

            * sha1
            * sha256
            * md5
            * md5sum
        """
        logger.debug("validating %s checksums" % (check_hash))

        for filename in self.get_files():
            if check_hash == "sha1":
                hash_type = hashlib.sha1()
                checksums = self.get("Checksums-Sha1")
                field_name = "sha1"
            elif check_hash == "sha256":
                hash_type = hashlib.sha256()
                checksums = self.get("Checksums-Sha256")
                field_name = "sha256"
            elif check_hash == "md5":
                hash_type = hashlib.md5()
                checksums = self.get("Files")
                field_name = "md5sum"

            for changed_files in checksums:
                if changed_files['name'] == os.path.basename(filename):
                    break
            else:
                assert(
                    "get_files() returns different files than Files: knows?!")

            with open(filename, "rb") as fc:
                while True:
                    chunk = fc.read(131072)
                    if not chunk:
                        break
                    hash_type.update(chunk)
            fc.close()

            if not hash_type.hexdigest() == changed_files[field_name]:
                raise ChangesFileException(
                    "Checksum mismatch for file %s: %s != %s" % (
                        filename,
                        hash_type.hexdigest(),
                        changed_files[field_name]
                    ))
            else:
                logger.trace("%s Checksum for file %s matches" % (
                    field_name, filename
                ))


def parse_changes_file(filename, directory=None):
    """
    Parse a .changes file and return a dput.changes.Change instance with
    parsed changes file data. The optional directory argument refers to the
    base directory where the referred files from the changes file are expected
    to be located.
    """
    _c = Changes(filename=filename)
    _c.set_directory(directory)
    return(_c)
