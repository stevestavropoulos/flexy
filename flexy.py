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

version="0.3pre"
execfile('utils.py')

usage = "Usage: %prog [-f <rules filename>] <word> <rule id>"
parser = OptionParser(usage=usage, version="%%prog %s" % version)
parser.add_option("-f", "--file", dest="filename", default='greek.py',
                  help="use FILE for rules definitions", metavar="FILE")
(options, args) = parser.parse_args()

if len(args) < 2:
	parser.error("Incorrect number of arguments")
if not os.path.isfile(options.filename):
	die("File %s doesn't exist!" % options.filename, 4)
else:
	execfile(options.filename)

word = args[0]
variation = args[1]

if variation not in rule:
	die("I don't know how to do technique %s" % variation, 5)

curule = rule[variation]
if 'actions' in curule:
	curule = {0: curule}
if 'preaction' in locals():
	word = preaction(word)
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
			searchy = defsearchy
			if searchkey in action:
				searchy = getRE(action[searchkey])
			doreplace = True
			if matchkey in action:
				doreplace = False
				if getRE(action[matchkey]).search(new):
					doreplace = True
			if doreplace:
				if replacekey in action:
					new = searchy.sub(action[replacekey], new)
		if 'callfunc' in action:
			new = action['callfunc'](new)
		if 'postaction' in locals():
			new = postaction(new)
		if isinstance(action['restype'], basestring):
			action['restype'] = [action['restype']]
		for result in action['restype']:
			print(new, result)
sys.exit(0)
