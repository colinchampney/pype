from types import SimpleNamespace
from importlib import import_module

class Underscore(SimpleNamespace):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.record = ""
		self.record_end = ""
		self.record_num = 0
		self.fields = None
		self.file   = None

	@property
	def R(self):
		return self.record

	@property
	def N(self):
		return self.record_num

	@property
	def F(self):
		return self.fields

	def __str__(self):
		return self.record
