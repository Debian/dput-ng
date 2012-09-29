
import ConfigParser
import os.path
import os

from libdput.misc import warning, error, set_debug_output, debug

(TYPE_STRING, TYPE_BOOLEAN, TYPE_HOSTNAME, TYPE_INTEGER) = range(0, 4)

class Stanza(object):
	# option name, option type, default value
	# [stanza]
	# 	fqdn	<any string>
	KEY_FQDN = ("fqdn", TYPE_STRING, None)
	# 	login	<any string>|*
	KEY_LOGIN = ("login", TYPE_STRING, None)
	# 	incoming	<any path>
	KEY_INCOMING = ("incoming", TYPE_STRING, None)
	# 	method	ftp|http|httpd|scp|rsync|local
	KEY_METHOD = ("method", TYPE_STRING, None)
	# 	hash	md5|sha1|sha256
	KEY_HASH = ("hash", TYPE_STRING, None)
	# 	allow_unsigned_uploads <boolean>
	KEY_ALLOW_UNSIGNED_UPLOADS = ("allow_unsigned_uploads", TYPE_BOOLEAN, False)
	# 	allow_dcut	<boolean>
	KEY_ALLOW_DCUT = ("allow_dcut", TYPE_BOOLEAN, True)
	# 	distributions	<any string>
	KEY_DISTRIBUTIONS = ("distributions", TYPE_STRING, None)
	# 	allowed_distributions	<regular expression>
	KEY_ALLOWED_DISTRIBUTIONS = ("allowed_distributions", TYPE_STRING, None)
	# 	delayed	<any numeric>
	KEY_DELAYED = ("delayed", TYPE_INTEGER, -1)
	# 	run_lintian <boolean>
	KEY_RUN_LINTIAN = ("run_lintian", TYPE_BOOLEAN, False)
	# 	run_dinstall <boolean>
	KEY_RUN_DINSTALL = ("run_dinstall", TYPE_BOOLEAN, False)
	# 	check_version <boolean>
	KEY_CHECK_VERSION = ("check_version", TYPE_BOOLEAN, False)
	# 	passive_ftp <boolean>
	KEY_PASSIVE_FTP = ("passive_ftp", TYPE_BOOLEAN, True)
	# 	progress_indicator 0|1|2
	KEY_PROGRESS_INDICATOR = ("progress_indicator", TYPE_INTEGER, 0)
	# 	scp_compress	<boolean>
	KEY_SCP_COMPRESS = ("scp_compress", TYPE_BOOLEAN, False)
	# 	ssh_config_options 
	KEY_SSH_CONFIG_OPTIONS = ("ssh_config_options", TYPE_STRING, None)
	# 	post_upload_command <any string>
	KEY_POST_UPLOAD_COMMAND = ("post_upload_command", TYPE_STRING, None)
	# 	pre_upload_command <any string>
	KEY_PRE_UPLOAD_COMMAND = ("pre_upload_command", TYPE_STRING, None)
	# 	default_host_main <any string>
	KEY_DEFAULT_HOST_MAIN = ("default_host_main", TYPE_STRING, None)

	def __init__(self, config, stanza_name):
		self._data = {}
		for item in dir(self):
			if not item.startswith("KEY_"):
				continue
			mangled_item = item.lower()[4:]
			item_object = getattr(self, item)
			try:
				if item_object[1] == TYPE_BOOLEAN:
					self._data[item_object[0]] = config.getboolean(stanza_name, mangled_item)
				else:
					self._data[item_object[0]] = config.get(stanza_name, mangled_item)
				#TODO: Validate configuration
			except ConfigParser.NoOptionError:
				self._data[item_object[0]] = item_object[2]
			except ValueError:
				error("Invalid configuration value in stanza %s for setting %s: `%s'" % (stanza_name, item_object[0], config.get(stanza_name, mangled_item)))

	def __getitem__(self, index):
		if not isinstance(index, tuple):
			raise KeyError("Invalid argument")
		return self._data[index[0]]

class Configurator(ConfigParser.ConfigParser):

	def __init__(self, debug_output=False):
		ConfigParser.ConfigParser.__init__(self)
		set_debug_output(debug_output)

	def get_upload_target(self, hostname):
		for stanza in self.sections():
			if stanza == hostname or (not hostname and self.get(stanza, "default_host_main")):
				debug("Picking stanza %s" % (stanza))
				return Stanza(self, stanza)
		else:
			error("Upload target `%s' was not found" % (hostname))

	def load_configuration(self, additional_configuration_file):
		config_files = ('/etc/dput.cf', os.path.expanduser("~/.dput.cf"))
		if additional_configuration_file:
			config_files.insert(0, additional_configuration_file)

		files_parsed = 0
		for config_file in config_files:
			if not os.access(config_file, os.R_OK):
				warning("Skipping file %s: Not accessible" % (config_file))
				continue
			try:
				_f = open(config_file)
				debug("Parsing %s" % (config_file))
				self.readfp(_f)
				_f.close()
				files_parsed += 1
			except IOError as e:
				warning("Skipping file %s: %s" % (config_file, e))
				continue
			except ConfigParser.ParsingError as e:
				error("Error parsing file %s: %s" % (config_file, e))

		if files_parsed == 0:
			error("Could not parse any configuration file: Tried %s" % (', '.join(config_files)))

