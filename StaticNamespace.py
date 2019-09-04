#!/usr/bin/env python3
import types

class StaticNamespace(types.SimpleNamespace):
	"""
	A simple namespace object with a static set of attributes. Similar to a named tuple, but mutable.
	Attributes and their default values are set with keyword arguments to the constructor.
	Attempting to set attributes that were not initialized by the constructor
	will result in an AttributeError. Attributes can not be deleted.
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		super().__setattr__("__input_map", tuple(kwargs.keys()))
	
	def __setattr__(self, name, value):
		if name not in self.__dict__:
			raise AttributeError("Can't set invalid attribute '%s'" % name)
		
		return super().__setattr__(name, value)
	
	def __delattr__(self, name):
		raise TypeError("StaticNamespace object does not support attribute deletion")
	
	def __getitem__(self, key):
		if not isinstance(key, int):
			raise TypeError("StaticNamespace object cannot be subscripted by non-integers")
		
		return self.__dict__[self.__input_map[key]]
	
	def __iter__(self):
		for attr in self.__input_map:
			yield self.__dict__[attr]