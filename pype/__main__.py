from pype.yieldfile import yield_from_files
from pype.underscore import Underscore
from pype.sandbox import ExecSandbox
import pype.argtypes as argt
import pype.util

import importlib
import argparse
import codeop
import sys
import re

argparser = argparse.ArgumentParser(prog="pype")

argparser.add_argument(
	"-p", "--printrecords",
	help="print each record after it is processed",
	action="store_true"
)
argparser.add_argument(
	"-n", "--nostrip",
	help="don't automatically strip newline characters from the end of each record",
	action="store_false",
	dest="strip"
)
argparser.add_argument(
	"-i", "--import",
	help="import the specified module. this option can be given multiple times",
	type=argt.ImportType,
	action="append",
	default=[],
	metavar="MODULE",
	dest="imports"
)
argparser.add_argument(
	"-r", "--recordsep",
	help="the characters that denote the end of a record (default behavior is Python's standard universal newline handling)",
	default=None,
	metavar="CHAR(S)",
)
argparser.add_argument(
	"-F", "--fieldsplit",
	help="split each record into fields using the given regex pattern as a delimiter",
	type=re.compile,
	default=None,
	metavar="PATTERN"
)

argparser_codeafter_group = argparser.add_mutually_exclusive_group()
argparser_codeafter_group.add_argument(
	"-A", "--run-after",
	help="run given code once AFTER all input is processed",
	type=argt.CompileStringType,
	metavar="CODE",
	dest="program_after"
)
argparser_codeafter_group.add_argument(
	"-Af", "--run-file-after",
	help="run given script file AFTER all input is processed",
	type=argt.CompileFileType,
	metavar="FILE",
	dest="program_after"
)

argparser_codebefore_group = argparser.add_mutually_exclusive_group()
argparser_codebefore_group.add_argument(
	"-B", "--run-before",
	help="run given code once BEFORE all input is processed",
	type=argt.CompileStringType,
	metavar="CODE",
	dest="program_before"
)
argparser_codebefore_group.add_argument(
	"-Bf", "--run-file-before",
	help="run given python script file BEFORE all input is processed",
	type=argt.CompileFileType,
	metavar="FILE",
	dest="program_before"
)

argparser_codegroup = argparser.add_mutually_exclusive_group(required=True)
argparser_codegroup.add_argument(
	"-c", "--program-code",
	help="code to run",
	type=argt.CompileStringType,
	metavar="CODE",
	dest="program"
)
argparser_codegroup.add_argument(
	"-f", "--program-file",
	help="file containing code",
	type=argt.CompileFileType,
	metavar="FILE",
	dest="program"
)

argparser.add_argument(
	"file",
	type=argparse.FileType('r'),
	nargs="*",
	default=[sys.stdin]
)

def main():
	args = argparser.parse_args()
	pype_underscore = Underscore()

	pype_globals = dict( args.imports )
	pype_globals["system"] = pype.util.import_from("os", "system")

	pype_sandbox = ExecSandbox(
		pype_globals,
		{ "_": pype_underscore }
	)

	if args.program_before:
		pype_sandbox.exec(args.program_before)


	record_num = 0
	for record_text, record_file in yield_from_files(*args.file, delimiter=args.recordsep):
		record_num += 1
		record_end = ""

		if args.strip:
			if args.recordsep is None:
				record_text, record_end = pype.util.separate_newline(record_text)
			else:
				record_text = record_text[:-len(args.recordsep)]
				record_end  = args.recordsep

		pype_underscore.record     = record_text
		pype_underscore.record_end = record_end
		pype_underscore.record_num = record_num
		pype_underscore.file       = record_file
		pype_underscore.fields     = args.fieldsplit.split(record_text) if args.fieldsplit else None

		pype_sandbox.exec(args.program)

		if args.printrecords:
			print(pype_underscore.record, end=pype_underscore.record_end)


	if args.program_after:
		pype_sandbox.exec(args.program_after)

if __name__ == "__main__":
	main()


























