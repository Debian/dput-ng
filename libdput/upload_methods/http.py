from libdput.upload_methods.base import BaseUpload
from libdput.config import Stanza as opt
from libdput.misc import debug, error, warning

class HTTPUpload(BaseUpload):

	def __init__(self, config):
		super(HTTPUpload, self).__init__(config)

	def initialize(self, **kwargs):
		pass

	def upload_file(self, filename):
		pass

	def shutdown(self):
		pass

class HTTPSUpload(HTTPUpload):
	pass
