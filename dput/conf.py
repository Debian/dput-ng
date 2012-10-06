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

import ConfigParser
import os

import dput.core
from dput.exceptions import DputConfigurationError

(TYPE_STRING, TYPE_BOOLEAN, TYPE_HOSTNAME, TYPE_INTEGER) = range(0, 4)


class Opt(object):
    """
    Hold parsed and validated configuration data for a particular dput.cf
    stanza. This class is merely a wrapper around a dictionary with additional
    type safety and last resort default case handling
    """
    # option name, option type, default value
    # [stanza]
    #       fqdn    <any string>
    KEY_FQDN = ("fqdn", TYPE_STRING, None)
    #       login   <any string>|*
    KEY_LOGIN = ("login", TYPE_STRING, None)
    #       incoming    <any path>
    KEY_INCOMING = ("incoming", TYPE_STRING, None)
    #       method  ftp|http|httpd|scp|rsync|local
    KEY_METHOD = ("method", TYPE_STRING, None)
    #       hash    md5|sha1|sha256
    KEY_HASH = ("hash", TYPE_STRING, "sha1")
    #       allow_unsigned_uploads <boolean>
    KEY_ALLOW_UNSIGNED_UPLOADS = ("allow_unsigned_uploads",
                                  TYPE_BOOLEAN, False)
    #       allow_dcut      <boolean>
    KEY_ALLOW_DCUT = ("allow_dcut", TYPE_BOOLEAN, True)
    #       distributions   <any string>
    KEY_DISTRIBUTIONS = ("distributions", TYPE_STRING, None)
    #       allowed_distributions   <regular expression>
    KEY_ALLOWED_DISTRIBUTIONS = ("allowed_distributions", TYPE_STRING, None)
    #       delayed <any numeric>
    KEY_DELAYED = ("delayed", TYPE_INTEGER, -1)
    #       run_lintian <boolean>
    KEY_RUN_LINTIAN = ("run_lintian", TYPE_BOOLEAN, False)
    #       run_dinstall <boolean>
    KEY_RUN_DINSTALL = ("run_dinstall", TYPE_BOOLEAN, False)
    #       check_version <boolean>
    KEY_CHECK_VERSION = ("check_version", TYPE_BOOLEAN, False)
    #       passive_ftp <boolean>
    KEY_PASSIVE_FTP = ("passive_ftp", TYPE_BOOLEAN, False)
    #       progress_indicator 0|1|2
    KEY_PROGRESS_INDICATOR = ("progress_indicator", TYPE_INTEGER, 0)
    #       scp_compress    <boolean>
    KEY_SCP_COMPRESS = ("scp_compress", TYPE_BOOLEAN, False)
    #       ssh_config_options
    KEY_SSH_CONFIG_OPTIONS = ("ssh_config_options", TYPE_STRING, None)
    #       post_upload_command <any string>
    KEY_POST_UPLOAD_COMMAND = ("post_upload_command", TYPE_STRING, None)
    #       pre_upload_command <any string>
    KEY_PRE_UPLOAD_COMMAND = ("pre_upload_command", TYPE_STRING, None)
    #       default_host_main <any string>
    KEY_DEFAULT_HOST_MAIN = ("default_host_main", TYPE_STRING, None)
    # sftp_private_key = <any string>
    KEY_SFTP_PRIVATE_KEY = ("sftp_private_key", TYPE_STRING, None)
    # sftp_username = <any string>
    KEY_SFTP_USERNAME = ("sftp_username", TYPE_STRING, None)
    # sftp_port = <any numeric>
    KEY_SFTP_PORT = ("sftp_port", TYPE_INTEGER, 22)

    def name(self):
        """
        Return the name of the stanza where this object was created from
        """
        return self._stanza

    def __init__(self, config, stanza_name):
        """
        Initialize the option set. Expected arguments are a ConfigParser
        object to load settings from, and the stanza name, which should be
        eventually represented in the object.
        """

        self._data = {}
        self._stanza = stanza_name
        for item in dir(self):
            if not item.startswith("KEY_"):
                continue
            mangled_item = item.lower()[4:]
            item_object = getattr(self, item)
            try:
                if item_object[1] == TYPE_BOOLEAN:
                    _value = config.getboolean(stanza_name, mangled_item)
                elif item_object[1] == TYPE_INTEGER:
                    _value = int(config.get(stanza_name, mangled_item))
                else:
                    _value = config.get(stanza_name, mangled_item)
                self._data[item_object[0]] = _value
                #TODO: Validate configuration
            except ConfigParser.NoOptionError:
                self._data[item_object[0]] = item_object[2]
            except ValueError:
                dput.core.logger.error(
                    "invalid value in stanza %s for setting %s: `%s'" % (
                        stanza_name,
                        item_object[0],
                        config.get(stanza_name, mangled_item)
                    )
                )

    def __contains__(self, item):
        return item in self._data

    def __getitem__(self, index):
        """
        Provide easy read access to option values.
        """

        # Convenience hack for Mr. Tag who prefers to use strings
        # This could also be cached to improve runtime performance
        if isinstance(index, tuple):
            return self._data[index[0]]
        else:
            for item in dir(self):
                if not item.startswith("KEY_") or (
                    item != "KEY_%s" % (index.upper())):
                        continue
                item_object = getattr(self, item)
                return self._data[item_object[0]]

    def __setitem__(self, index, value):
        """
        Provide easy write access to option values.
        """
        if not isinstance(index, tuple):
            index = (index,)
        self._data[index[0]] = value

    def __repr__(self):
        return self._data.__repr__()


def get_upload_target(conf, hostname):
    """
    Pick up the configuration associated with the upload target where we are
    supposed to upload. Falls back to "ftp-master" if no target was given.
    """
    selected_stanza = None
    fallback_stanza = "ftp-master"

    for stanza in conf.sections():
        if stanza == hostname:
            selected_stanza = stanza
            break
        if not hostname and conf.get(stanza, "default_host_main"):
            selected_stanza = stanza
            break
    if not hostname and conf.has_section(fallback_stanza):
        selected_stanza = fallback_stanza

    if selected_stanza:
        dput.core.logger.debug("Picking stanza %s" % (selected_stanza))
        return Opt(conf, selected_stanza)
    else:
        raise DputConfigurationError("Upload target `%s' was not found"
                                     % (hostname))


def load_configuration(configuration_files, replacements):
    """
    Load all the dput config files to take action in a sane way. The argument
    ```configuration_files``` is a list of files to search, and if found,
    attempts to parse the key/value pairs. Each subsequent file may override
    the last.

    Special-cased handling on the blocked labeled "DEFAULT" allows that to
    serve as an underlay for missing keys.

    """
    files_parsed = 0
    parser = ConfigParser.ConfigParser()
    for config_file in configuration_files:
        if not os.access(config_file, os.R_OK):
            dput.core.logger.warning("Skipping file %s: Not accessible" % (
                config_file))
            continue
        try:
            _f = open(config_file)
            dput.core.logger.debug("Parsing %s" % (config_file))
            parser.readfp(_f)
            _f.close()
            files_parsed += 1
        except IOError as e:
            dput.core.logger.warning("Skipping file %s: %s" % (config_file, e))
            continue
        except ConfigParser.ParsingError as e:
            raise DputConfigurationError(
                            "Error parsing file %s: %s" % (config_file, e))

    if files_parsed == 0:
        raise DputConfigurationError(
                    "Could not parse any configuration file: Tried %s" %
                    (', '.join(configuration_files)))

    for replacement in replacements:
        parser.set(replacement, replacement, replacements[replacement])

    return parser


def load_dput_configs(upload_target):
    """
    Load the dput configuration file for the target stanza ```upload_target```.
    Internally, this checks for each file `dput.core.DPUT_CONFIG_LOCATIONS`
    for a matching stanza and inherits defaults from deriving parent stanzas.

    Returns a Stanza object with stanza settings.
    """

    repls = {}
    if ":" in upload_target:
        upload_target, arg = upload_target.split(":", 1)
        repls[upload_target] = arg

    dput.core.logger.debug("Loading dput configs")
    # TODO: Where/How to handle exceptions?
    _conf = load_configuration(dput.core.DPUT_CONFIG_LOCATIONS, repls)
    ret = get_upload_target(_conf, upload_target)
    return ret
