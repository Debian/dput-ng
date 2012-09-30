import ftplib
import os.path

from libdput.upload_methods.base import BaseUpload
from libdput.config import Stanza as opt
from libdput.misc import debug, error, warning

class FTPUpload(BaseUpload):

	def __init__(self, config):
		super(FTPUpload, self).__init__(config)
		try:
			self._ftp = ftplib.FTP(self._config[opt.KEY_FQDN], self._config[opt.KEY_LOGIN], None, timeout=10)
		except Exception as e:
			error("Could not establish FTP connection to %s: %s" % (self._config[opt.KEY_FQDN], e))

	def initialize(self, **kwargs):
		if self._config[opt.KEY_PASSIVE_FTP]:
			debug("Enable PASV mode")
			self._ftp.set_pasv(True)
		if self._config[opt.KEY_INCOMING]:
			debug("Change directory to %s" % (self._config[opt.KEY_INCOMING]))
			self._ftp.cwd(self._config[opt.KEY_INCOMING])

	def upload_file(self, filename):
		try:
			basename = "STOR %s" % (os.path.basename(filename))
			self._ftp.storbinary(basename, open(filename, 'rb'))
		except ftplib.error_perm as e:
			#TODO: Steal dput's warning here.
			warning("Could not overwrite file. blah blah blah")
		except Exception as e:
			error("Could not upload file %s: %s" % (filename, e))

	def shutdown(self):
		self._ftp.quit()
