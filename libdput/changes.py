# -*- coding: utf-8 -*-
#
#   changes.py — .changes file handling class
#
#   This file was originally part of debexpo - https://alioth.debian.org/projects/debexpo/
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#   Copyright © 2012 Arno Töll <arno@debian.org>
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
Holds *changes* file handling class.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

from debian import deb822
from libdput.misc import debug

import os.path
import hashlib
import subprocess

class Changes(object):
	"""
	Helper class to parse *changes* files nicely.
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
			self._data = deb822.Changes(file(filename))
		else:
			self._data = deb822.Changes(string)

		if len(self._data) == 0:
			raise Exception('Changes file could not be parsed.')
		if filename:
			self.basename = os.path.basename(filename)
		else:
			self.basename = None

	def get_filename(self):
		"""
		Returns the filename from which the changes file was generated from
		"""
		return self.basename

	def get_changes_file(self):
		return os.path.join(self._directory, self.get_filename())

	def get_files(self):
		"""
		Returns a list of files in the *changes* file.
		"""
		return [os.path.join(self._directory, z['name']) for z in self._data['Files']]

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

	def _parse_section(self, section):
		"""
		Works out the component and section from the "Section" field.
		Sections like `python` or `libdevel` are in main.
		Sections with a prefix, separated with a forward-slash also show the component.
		It returns a list of strings in the form [component, section].

		For example, `non-free/python` has component `non-free` and section `python`.

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
		self.validate_checksums(check_hash)
		self.validate_signature(check_signature)

	def validate_signature(self, check_signature=True):
		gpg_path = "/usr/bin/gpg"
		if os.access(gpg_path, os.R_OK):
			pipe = subprocess.Popen("%s --status-fd 1 --verify --batch %s" % (gpg_path, self.get_changes_file()),
								shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(gpg_output, gpg_output_stderr) = pipe.communicate()
			if pipe.returncode != 0:
				raise Exception("%s returned failure: %s" % (gpg_output_stderr))

			# contains verbose human readable GPG information
			print(gpg_output_stderr)

			if gpg_output.count('[GNUPG:] GOODSIG'):
				pass
			elif gpg_output.count('[GNUPG:] BADSIG'):
				raise Exception("Bad signature")
			elif gpg_output.count('[GNUPG:] ERRSIG'):
				raise Exception("Error verifying signature")
			elif gpg_output.count('[GNUPG:] NODATA'):
				raise Exception("No signature on")
			else:
				raise Exception("Unknown problem while verifying signature")

		else:
			raise Exception("Could not find /usr/bin/gpg to verify the signature")

	def validate_checksums(self, check_hash="sha1"):
		debug("Validate %s checksums" % (check_hash))

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
				assert("get_files() returns different files than Files: knows?!")


			with open(filename, "r") as fc:
				while True:
					chunk = fc.read(131072)
					if not chunk:
						break
					hash_type.update(chunk)
			fc.close()

			if not hash_type.hexdigest() == changed_files[field_name]:
				raise Exception("Checksum mismatch for file %s: %s != %s" % (filename, hash_type.hexdigest(), changed_files[field_name]))
			else:
				debug("%s Checksum for file %s matches" % (field_name, filename))
