import paramiko
import os.path

#paramiko.util.log_to_file('/tmp/paramiko.log')

from libdput.upload_methods.base import BaseUpload
from libdput.config import Stanza as opt
from libdput.misc import debug, error, warning

class SFTPUpload(BaseUpload):

	def __init__(self, config):
		super(SFTPUpload, self).__init__(config)

	def initialize(self, **kwargs):
		self._transport = paramiko.Transport((self._config[opt.KEY_FQDN], self._config[opt.KEY_SFTP_PORT]))

		try:
			private_key = None
			if self._config[opt.KEY_SFTP_PRIVATE_KEY]:
				if self._config[opt.KEY_SFTP_PRIVATE_KEY].startswith("~"):
					private_key_file = os.path.expanduser(self._config[opt.KEY_SFTP_PRIVATE_KEY])
				else:
					private_key_file = self._config[opt.KEY_SFTP_PRIVATE_KEY]
				debug("Authenticate using private key %s" % (private_key_file))

				if not os.access(private_key_file, os.R_OK):
					error("Key file %s is not accessible" % (private_key_file))
				private_key = paramiko.RSAKey.from_private_key_file(private_key_file)

			user = self._config[opt.KEY_SFTP_USERNAME]
			password = None

			debug("SFTP user: %s; password: %s" % (user, "YES" if password else "NO"))

			self._transport.connect(username=user, password=password, pkey=private_key)
			self._sftp = paramiko.SFTPClient.from_transport(self._transport)
		except paramiko.AuthenticationException as e:
			error("Failed to authenticate with server %s: %s" % (self._config[opt.KEY_FQDN], e))


		try:
			self._sftp.chdir(self._config[opt.KEY_INCOMING])
		except IOError as e:
			error("Could not change directory to %s: %s" % (self._config[opt.KEY_INCOMING], e))

	def upload_file(self, filename):
		basename = os.path.basename(filename)
		try:
			self._sftp.put(basename, filename)
		except IOError as e:
			if e.errno == 13:
				warning("Could not overwrite file. blah blah blah")
			else:
				error("Could not upload file %s: %s" % (filename, e))

	def shutdown(self):
		self._sftp.close()
		self._transport.close()
