import abc

class BaseUpload(object):
	__metaclass__ = abc.ABCMeta

	def __init__(self, config):
		self._config = config

	@abc.abstractmethod
	def initialize(self, **kwargs):
		pass

	@abc.abstractmethod
	def upload_file(self, filename):
		pass

	@abc.abstractmethod
	def shutdown(self):
		pass
