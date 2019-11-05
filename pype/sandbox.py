class ExecSandbox():
	def __init__(self, globls=None, locls=None, imports=None):
		self.globals = copy.copy(globals()) if globls is None else globls
		self.locals = copy.copy(locals()) if locls is None else locls
		
		if imports:
			self.import_modules(imports)
	
	def __call__(self, codeobj):
		return self.exec(codeobj)
	
	def exec(self, codeobj):
		return exec(codeobj, self.globals, self.locals)
	
	def import_modules(self, modules):
		for mod_str in modules:
			mod = importlib.import_module(mod_str)
			self.globals[mod.__name__] = mod
	
	def import_from_module(self, module, attrs):
		for attr_name in attrs:
			attr = getattr(importlib.import_module(module), attr_name)
			self.globals[attr.__name__] = attr