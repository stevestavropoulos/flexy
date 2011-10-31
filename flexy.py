#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Flexy - Tool to inflect and in other ways "flex" words
#
#   Version 0.3pre
#
#   Copyright 2006,2009,2011 Steve Stavropoulos <steve@math.upatras.gr>
#
#   This file is part of Flexy.
#
#   Flexy is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Flexy is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Flexy.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import os, re, sys, string
from optparse import OptionParser
from utils import *
version="0.3pre"

def flexit(word, variation, langdef):
	if variation not in langdef.rules:
		die("I don't know how to do technique %s" % variation, 5)
	if method_exists(langdef, 'preaction'):
		word = langdef.preaction(word)
	curule = langdef.rules[variation]
	if 'actions' in curule:
		curule = {0: curule}
	for variationkey, detail in curule.iteritems():
		matchpattern = defsearchy = getRE(detail['match'])
		if 'search' in detail:
			defsearchy = getRE(detail['search'])
		if not matchpattern.search(word):
			continue
		for action in detail['actions']:
			new = word
			for i in ['', '2']:
				searchkey = 'search' + i
				matchkey = 'match' + i
				replacekey = 'replace' + i
				if method_exists(langdef, 'preaction'):
					for tmp in [searchkey, matchkey, replacekey]:
						if tmp in action:
							action[tmp] = langdef.preaction(action[tmp])
				searchy = defsearchy
				if searchkey in action:
					searchy = getRE(action[searchkey])
				doreplace = True
				if matchkey in action:
					doreplace = False
					if getRE(action[matchkey]).search(new):
						doreplace = True
				if doreplace and replacekey in action:
					new = searchy.sub(action[replacekey], new)
			if 'callfunc' in action:
				new = action['callfunc'](new)
			if method_exists(langdef, 'postaction'):
				new = langdef.postaction(new)
			if isinstance(action['restype'], basestring):
				action['restype'] = [action['restype']]
			for result in action['restype']:
				print(new, result)

usage = "Usage: %prog [<options>] <word> [<rule id>]"
parser = OptionParser(usage=usage, version="%%prog %s" % version)
parser.add_option("-l", "--language", dest="language", default='greek',
                  help="use LANGUAGE for rules definitions", metavar="LANGUAGE")
(options, args) = parser.parse_args()

if len(args) < 1:
	parser.error("Incorrect number of arguments")
if not os.path.isfile(options.language + '.py'):
	die("File %s doesn't exist!" % options.language + '.py', 4)
else:
	exec("import " + options.language + " as langdef")

word = args[0]
if len(args) >= 2:
	flexit(word, args[1], langdef)
else:
	for avariation in langdef.rules:
		flexit(word, avariation, langdef)
