import re

from libdput.misc import run_command, warning, debug, error
from libdput.changes import Changes

class SanityException(BaseException):
	pass

def check_distribution(changes):
	assert(isinstance(changes, Changes))

	changelog_distribution = changes.get("Changes").split()[2].strip(';')

	if not len(changelog_distribution):
		raise SanityException("Unexpected changelog entry?")

	if not changelog_distribution == changes.get("Distribution"):
		raise SanityException("Target distribution does not match changelog: %s != %s" % (changelog_distribution, changes.get("Distribution")))

# check whether -sa was missing when building the changes files
def check_source_needed(changes):
	assert(isinstance(changes, Changes))

	debian_revision = changes.get("Version")
	if debian_revision.find("-") == -1:
		debug("Package appears to be native")
		return
	debug("Package appears to be non-native")

	debian_revision = debian_revision[debian_revision.rfind("-") + 1:]
	debian_revision = int(debian_revision)
	# policy 5.6.12:
	# debian_revision --
	# It is optional; if it isn't present then the upstream_version may not contain a hyphen.
	# This format represents the case where a piece of software was written specifically to be a
	# Debian package, where the Debian package source must always be identical to the pristine source
	# and therefore no revision indication is required.

	orig_tarball_found = False
	for filename in changes.get_files():
		if re.search("orig\.tar\.(gz|bz2|lzma|xz)$", filename):
			orig_tarball_found = True
			break

	if debian_revision == 1 and not orig_tarball_found:
		raise SanityException("Upload appears to be a new upstream version but does not include original tarball")
	elif debian_revision > 1 and orig_tarball_found:
		warning("Upload appears to be a Debian specific change, but does include original tarball")

def run_lintian(changes_file):
	lintian_path = "lintian"
	debug("Running Lintian")
	(lintian_out, lintian_err, return_code) = run_command([lintian_path, "-I", changes_file])
	debug(lintian_out)
	if return_code == 1:
		raise SanityException("%s\nLintian reports policy violations" % (lintian_out))
	if return_code == 2:
		error("Lintian reported a run-time error: %s" % (lintian_err))

def run_piuparts(changes_file):
	pass

def run_dinstall():
	pass
