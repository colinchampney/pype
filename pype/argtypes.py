from importlib import import_module
from collections import namedtuple
import argparse
import re

def FileReadType(filename):
	try:
		return open(filename, 'r')
	except (FileNotFoundError, OSError) as e:
		raise argparse.ArgumentTypeError( str(e) )

def CompileStringType(code, filename="<string>"):
	try:
		return compile(code, filename, "exec")
	except Exception as e:
		raise argparse.ArgumentTypeError( str(e) )

def CompileFileType(filename):
	try:
		with open(filename, 'r') as f:
			return CompileStringType(f.read(), f.name)
	except (FileNotFoundError, OSError) as e:
		raise argparse.ArgumentTypeError( str(e) )

importspec = re.compile(r"(\w+)(?::(\w+))?(?:@(\w+))?")
def ImportType(import_str):
	module, component, as_name = importspec.match(import_str).groups()

	try:
		target = import_module(module)
		target_name = module
		if component:
			target = getattr(target, component)
			target_name = component
	except (ModuleNotFoundError, AttributeError) as e:
		raise argparse.ArgumentTypeError( str(e) )

	return as_name or target_name, target_name