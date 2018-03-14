#!/usr/bin/env python3
import importlib
import argparse
import types
import copy
import sys
import re
import os

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

class StaticNamespace(types.SimpleNamespace):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
	
	def __setattr__(self, name, value):
		if name not in self.__dict__:
			raise AttributeError("Can't set invalid attribute '{}'".format(name))
		
		return super().__setattr__(name, value)
	
	def __delattr__(self, name):
		raise TypeError("StaticNamespace object does not support item deletion")

def readuntil(file, delimiter):
	i = 0
	chars = []
	
	if not delimiter:
		return file.read()
	
	while True:
		char = file.read(1)
		chars.append(char)
		
		if char == '':
			break
		
		if char == delimiter[i]:
			i += 1
			if i == len(delimiter):
				break		
		else:
			i = 0
	
	return ''.join(chars)

def yield_from_files(*files, delimiter="\n"):
	for f in files:
		while True:
			line = readuntil(f,delimiter)
			if line == '':
				break
			
			yield (line, f)

def FileReadType(filename):
	try:
		return open(filename, 'r')
	except FileNotFoundError as e:
		raise argparse.ArgumentTypeError("can't open '{}': file does not exist".format(file))
	except OSError as e:
		raise ArgumentTypeError("can't open '{}': {}".format(filename, e))

def CompileStringType(code, filename="<string>"):
	try:
		return compile(code, filename, "exec")
	except Exception as e:
		raise argparse.ArgumentTypeError(e)

def CompileFileType(filename):
	try:
		with open(filename, 'r') as f:
			return CompileStringType(f.read(), f.name)
	except FileNotFoundError as e:
		raise argparse.ArgumentTypeError("can't open '{}': file does not exist".format(filename))
	except OSError as e:
		raise argparse.ArgumentTypeError(e)


if __name__ == "__main__":
	## PARSE ARGUMENTS ##
	argparser = argparse.ArgumentParser(prog="pype")
	
	argparser.add_argument(
		"-p", "--printlines",
		help="print each line after it is processed",
		action="store_true"
	)
	argparser.add_argument(
		"-n", "--nostrip",
		help="don't automatically strip newline characters from the end of each line",
		action="store_false",
		dest="strip"
	)
	argparser.add_argument(
		"-i", "--import",
		help="import the specified module. this option can be given multiple times",
		action="append",
		default=[],
		metavar="MODULE",
		dest="modules"
	)
	argparser.add_argument(
		"-F", "--fieldsplit",
		help="split each line into fields using the given pattern as a delimiter",
		type=re.compile,
		default=None,
		metavar="PATTERN"
	)
	
	argparser_codeafter_group = argparser.add_mutually_exclusive_group()
	argparser_codeafter_group.add_argument(
		"-A", "--run-after",
		help="run given code once AFTER all input is processed",
		type=CompileStringType,
		metavar="CODE",
		dest="program_after"
	)
	argparser_codeafter_group.add_argument(
		"-Af", "--run-file-after",
		help="run given script file AFTER all input is processed",
		type=CompileFileType,
		metavar="FILE",
		dest="program_after"
	)
	
	argparser_codebefore_group = argparser.add_mutually_exclusive_group()
	argparser_codebefore_group.add_argument(
		"-B", "--run-before",
		help="run given code once BEFORE all input is processed",
		type=CompileStringType,
		metavar="CODE",
		dest="program_before"
	)
	argparser_codebefore_group.add_argument(
		"-Bf", "--run-file-before",
		help="run given python script file BEFORE all input is processed",
		type=CompileFileType,
		metavar="FILE",
		dest="program_before"
	)
	
	argparser_codegroup = argparser.add_mutually_exclusive_group(required=True)
	argparser_codegroup.add_argument(
		"-c", "--program-code",
		help="code to run",
		type=CompileStringType,
		metavar="CODE",
		dest="program"
	)
	argparser_codegroup.add_argument(
		"-f", "--program-file",
		help="file containing code",
		type=CompileFileType,
		metavar="FILE",
		dest="program"
	)
	
	argparser.add_argument(
		"file",
		type=argparse.FileType('r'),
		nargs="*",
		default=[sys.stdin]
	)

	args = argparser.parse_args()


	## INITIALIZE EXEC SANDBOX ##
	line_data = StaticNamespace(
		line = None,
		line_num = 0,
		line_fields = None,
		file = None,
		end = False
	)
	
	try:
		exec_sandbox = ExecSandbox(
			{"__builtins__": __builtins__},
			{"_": line_data},
			args.modules
		)
	except ModuleNotFoundError as e:
		argparser.error(e)
	
	#alias for sandbox locals to make it easier to reference later
	line_data = exec_sandbox.locals["_"]
	

	## EXECUTE PROGRAM FOR EACH LINE ##
	#if "-B" option given, execute given code before anything else
	if args.program_before:
		exec_sandbox(args.program_before)
	
	#run for each file
	for line, line_data.file in yield_from_files(*args.file):	
		if line_data.end:
			break
		
		#increment _.line_num, starts at 0 before any lines are read
		line_data.line_num += 1
		
		#set current _.line value, removing newline char(s) unless '-n' flag is set
		line_data.line = line.rstrip(os.linesep) if args.strip else line
		
		#if '-f pattern' option given, split line into fields based on pattern
		#store fields in _.line_fields list
		if args.fieldsplit:
			line_data.line_fields = args.fieldsplit.split(line_data.line)
		
		#execute given program argument
		exec_sandbox(args.program)
		
		#if '-p' flag set, print _.line by default
		if args.printlines:
			print(
				line_data.line,
				end=os.linesep if args.strip else ""
			)
	
	if args.program_after:
		exec_sandbox(args.program_after)
	
	for f in args.file:
		f.close()