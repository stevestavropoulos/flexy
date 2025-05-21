# -*- coding: utf-8 -*-

from __future__ import print_function
import re, sys, string

def getRE(pattern):
	return re.compile(pattern, re.I)

def tr(fr, to, word):
	"""poor man's unicode translate"""
	new = []
	for letter in word:
		pos = fr.find(letter)
		if pos != -1:
			new.append(to[pos])
		else:
			new.append(letter)
	return ''.join(new)

def die(msg, exitcode=1):
	print(msg)
	sys.exit(exitcode)

def method_exists(classname, methodname):
	if hasattr(classname, methodname) and callable(getattr(classname, methodname)):
		return True
	return False

