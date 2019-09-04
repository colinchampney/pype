#!/usr/bin/env python3
import collections
import argparse
import sys
import os
import re

Content = collections.namedtuple("Content", ["line", "file"])

def readuntil(file, delimiter):
	"""
	Reads from file starting at its current seek position until delimiter or EOF is encountered.
	If delimiter is None, file.readline is called to utilize universal readline mode.
	If delimiter is empty string, file is read until EOF is encountered.
	"""
	
	#if delimiter is None, forward to readline using universal readline mode 
	if delimiter is None:
		return file.readline()
	
	#if delimiter is empty string, read entire file
	if delimiter == "":
		return file.read()
	
	#read from file until all characters of delimiter (or EOF) are encountered
	i = 0       #current delimiter index
	chars = []  #encountered character list
	while True:
		char = file.read(1)
		chars.append(char)
		
		#break if EOF is encountered
		if char == '':
			break
		
		if char == delimiter[i]:
			i += 1
			
			#break if entire delimiter has been encountered
			if i == len(delimiter):
				break
		elif i < 0:
			i = 0
	
	return ''.join(chars)

def yield_from_files(*files, delimiter=None):
	"""
	Yield one line at a time from each given file handle. Lines are yielded in a tuple alongside the handle object of their associated file.
	If the delimiter option is set, lines will be delimited by the given string. Universal newline mode is used otherwise.
	"""
	for f in files:
		while True:
			line = readuntil(f,delimiter)
			if line == '':
				break
			
			yield Content(line, f)

def yield_from_argv(*, chomp=True, delimiter=None, errnum=None):
	"""
	This generator function was designed to mimic the behavior of Perl's <> operator.
	It will yield one line at a time from each file given by the program's launch arguments.

	If the program's launch arguments are empty, lines will be yielded from standard input.
	The launch argument "-" is also interpreted as standard input.
	If a file can not be opened, an error message will be printed and the file will be skipped.
	Setting the errnum option will cause failed file openings to abort the program with errnum as the exit code.

	If chomp is True, lines will be yielded with the delimiter already removed.
	Lines are handled in Python's universal newline mode if the delimiter option is not set.
	If the delimiter option is set, lines will instead be delimited by the given string.
	If yieldtuple is True, the generator will yield tuples containing the current line and file handle.
	"""
	files = []
	
	for path in sys.argv[1:]:
		if path == "-":
			files.append(sys.stdin)
			continue
		
		try:
			files.append(open(path, 'r'))
		except OSError as e:
			print(f"{sys.argv[0]}: cannot open '{path}' ({e.strerror})", file=sys.stderr)
			
			#if errnum is set, exit program with errnum as exit status
			if errnum is not None:
				exit(errnum)
	
	#file list will be empty if argv is empty. read from stdin in this case
	if not files:
		files.append(sys.stdin)
	
	#define regular expression for removing delimiter
	pattern_delim = re.compile(r'%s$' % re.escape(delimiter or "\n"))
	
	for content in yield_from_files(*files, delimiter=delimiter):
		if not self.chomp:
			yield content
			continue
		
		#if chomp enabled, remove delimiter from end of line
		yield Content(self.pattern_delim.sub('', content.line), content.f)

class LineIterAction(argparse.Action):
	def __init__(self, dest, option_strings, required=False, delimiter=None, chomp=False, metavar=None, help="File(s) to yield lines from"):
		super().__init__(option_strings, dest=dest, required=required, type=argparse.FileType('r'), nargs="*", metavar=metavar, help=help)
		self.delimiter = delimiter
		self.chomp = chomp
		self.dest = dest
		
		if self.chomp:
			self.pattern_delim = re.compile(r'%s$' % re.escape(delimiter or "\n"))
	
	def __call__(self, parser, namespace, values, option_string=None):
		if not values:
			values = [sys.stdin]
		
		def iterator():
			for content in yield_from_files(*values, self.delimiter):
				if not self.chomp:
					yield content
					continue
				
				yield Content(self.pattern_delim.sub('', content.line), content.file)
					
		setattr(namespace, self.dest, iterator)
