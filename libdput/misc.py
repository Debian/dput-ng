from __future__ import print_function

import sys
import subprocess

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


def run_command(command):
	assert(isinstance(command, list))
	try:
		pipe = subprocess.Popen(command,
							shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except OSError as e:
		error("Could not execute %s: %s" % (" ".join(command), e))
	(output, stderr) = pipe.communicate()
	#if pipe.returncode != 0:
	#	error("Command %s returned failure: %s" % (" ".join(command), stderr))
	return (output, stderr, pipe.returncode)
