#!/usr/bin/env python3
import functools
import argparse
import sys
import re
import os
from yieldfile import readuntil, yield_from_files, Content
from StaticNamespace import StaticNamespace
from ExecSandbox import ExecSandbox

def re_partition(pattern, string):
	re_search = None
	
	if isinstance(pattern, re._pattern_type):
		re_search = pattern.search
	else:
		re_search = functools.partial(re.search, pattern)
	
	match = re_search(string)
	if not match:
		return (string, None, None)
	
	return (
		string[:match.start()],
		match.group(),
		string[match.end():]
	)

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

def parse_arguments(*args):
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
		"-l", "--linesep",
		help="the characters that denote the end of a line (default behavior is Python's standard universal newline handling)",
		default=None,
		metavar="CHAR(S)",
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

	return argparser.parse_args(args or None)
	

if __name__ == "__main__":
	## PARSE ARGUMENTS ##
	args = parse_arguments()


	## INITIALIZE EXEC SANDBOX ##
	#set up line data namespace for user program
	line_data = StaticNamespace(
		line        = None,
		line_num    = 0,
		line_fields = None,
		file        = None,
		end         = False
	)
	
	#create ExecSandbox object with line data namespace in locals
	exec_sandbox = ExecSandbox(
		{},
		{"_": line_data},
	)
	
	#try to import specified modules
	try:
		exec_sandbox.import_modules(args.modules)
	except ModuleNotFoundError as e:
		argparser.error(e)
	
	
	## COMPILE REGULAR EXPRESSIONS FOR LINE ENDINGS ##
	line_sep = None
	if args.strip:
		#if args.linesep is None, assume Python's universal newline handling is being used
		if args.linesep is None:
			line_sep = re.compile(r"\n$")
		else:
			line_sep = re.compile(f"{re.escape(args.linesep)}$")
			

	## EXECUTE USER PROGRAM ##
	#if "-B" option given, execute given code before anything else
	if args.program_before:
		exec_sandbox(args.program_before)
	
	#execute user program for each line in each file
	for line, line_data.file in yield_from_files(*args.file, delimiter=args.linesep):
		#if input code has set _.end, end loop
		if line_data.end:
			break
		
		#increment _.line_num, starts at 0 before any lines are read
		line_data.line_num += 1
		
		#perform separation of line end if -n is not set
		line_begin = None
		line_end = None
		if args.strip:
			line_begin, line_end, _ = re_partition(line_sep, line)
		
		#set current _.line value, removing line end char(s) unless '-n' flag is set
		line_data.line = line_begin if args.strip else line
		
		#if '-f PATTERN' option given, split line into fields based on pattern
		#store fields in _.line_fields list
		if args.fieldsplit:
			line_data.line_fields = args.fieldsplit.split(line_data.line)
		
		#execute user program on current line
		exec_sandbox(args.program)
		
		#if '-p' flag set, print _.line by default
		if args.printlines:
			#set end parameter for print function
			#if -n was NOT given, line end was stripped. print end parameter will be line_end if it was found, otherwise empty string
			#if -n was given, line end was not stripped. print end parameter will be empty string
			print_end = line_end if (args.strip and line_end is not None) else ""
			
			print(
				line_data.line,
				end=print_end
			)
	
	#if "-A" option given, execute given code after anything else
	if args.program_after:
		exec_sandbox(args.program_after)
	
	
	## CLOSE FILES ##
	for f in args.file:
		f.close()