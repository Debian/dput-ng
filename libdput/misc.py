from __future__ import print_function

import sys

def warning(the_message):
	print(the_message, file=sys.stderr)

def error(the_message):
	print(the_message, file=sys.stderr)
	sys.exit(1)

__DEBUG__ = False

def set_debug_output(flag):
	global __DEBUG__
	__DEBUG__ = flag
	debug("Enable debugging output")

def debug(the_message):
	global __DEBUG__
	if __DEBUG__:
		print(the_message, file=sys.stderr)
