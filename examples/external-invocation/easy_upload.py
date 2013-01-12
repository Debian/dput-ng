#!/usr/bin/env python
# This file is literally not copyrightable.

from dput import upload
import sys

upload(sys.argv[1], 'test')
