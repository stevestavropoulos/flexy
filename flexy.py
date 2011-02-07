#!/usr/bin/env python
# -*- coding: iso-8859-7 -*-
#
#   Flexy - Tool to inflect and in other ways "flex" words
#
#   Version 0.2
#
#   Copyright 2006,2009 Steve Stavropoulos <steve@math.upatras.gr>
#
#   This file is part of Flexy.
#
#   Flexy is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Foobar is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import os, re, sys, string

def getRE(patttern):
	return re.compile(patttern, re.I | re.L)

if len(sys.argv) > 3:
	filename = sys.argv[3]
else:
	filename = 'greek.py'
word = sys.argv[1]
variation = sys.argv[2]
if not filename or not os.path.isfile(filename):
	print 'Filename', filename, "doesn't exist!"
	sys.exit(1)
else:
	execfile(filename)

if variation not in rule:
	print "I don't know how to do technique", variation
	sys.exit(2)

curule = rule[variation]
if 'actions' in curule:
	curule = {0: curule}
if 'preaction' in locals():
	word = preaction(word)
for variation, detail in curule.iteritems():
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
			if searchkey in action:
				searchy = getRE(action[searchkey])
			else:
				searchy = defsearchy
			if matchkey in action:
				if getRE(action[matchkey]).search(word):
					dosub = True
				else:
					dosub = False
			else:
				dosub = True
			if dosub:
				if replacekey in action:
					new = searchy.sub(action[replacekey], new)
		if 'callfunc' in action:
			new = action['callfunc'](new)
		if 'postaction' in locals():
			new = postaction(new)
		if isinstance(action['restype'], basestring):
			action['restype'] = [action['restype']]
		for result in action['restype']:
			print new, result
sys.exit(0)
