from importlib import import_module
import re

pattern_newline = re.compile(r"(\n|\r\n|\r)$")
def separate_newline(line):
	match = pattern_newline.search(line)
	line_content = line[:match.start() if match else len(line)]
	line_end     = match.group() if match else ""

	return line_content, line_end

def import_from(module_name, member_name):
	module = import_module(module_name)
	return getattr( module, member_name )
